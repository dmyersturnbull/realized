# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0


import re
import typing
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import timedelta
from typing import Self, TypeVar, Generic, ClassVar

from realized.dt.durations import Duration
from realized._core import Model, JsonType
from realized.dt.instants import Instant

__all__ = ["RepeatInterval", "RepeatEvent", "RepeatDuration"]
REPEAT_REGEX = re.compile(r"^R(\d*)/(.+)$")
I_co = TypeVar("I_co", bound=Instant, covariant=True)
D_co = TypeVar("D_co", bound=Duration, covariant=True)


@dataclass(slots=True, frozen=True, order=True)
class RepeatInterval(Model, Generic[I_co]):

    start: I_co
    end: I_co
    repeats: int | None

    @classmethod
    def instant_type(cls: type[Self]) -> type[I_co]:
        return typing.get_args(cls)[0]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        m = REPEAT_REGEX.fullmatch(s)
        repeat = m.group(1)
        start, end = m.group(2).split("--")
        return cls(start, end, repeat)

    @property
    def as_str(self: Self) -> str:
        r = "" if self.repeats is None else self.repeats
        return f"R{r}/{self.start}--{self.end}"

    @property
    def duration(self: Self) -> Duration:
        return Duration(self.end.dt - self.start.dt)

    @property
    def _json_data(self: Self) -> JsonType:
        return {
            "interval": self.start.as_str,
            "end": self.end.as_str,
            "repeats": self.repeats
        }


@dataclass(slots=True, frozen=True, order=True)
class RepeatEvent(Model, Generic[D_co]):

    duration: D_co
    repeats: int | None

    @classmethod
    def duration_type(cls: type[Self]) -> type[D_co]:
        return typing.get_args(cls)[0]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        m = REPEAT_REGEX.fullmatch(s)
        repeat = int(m.group(1))
        duration = m.group(2)
        return cls(duration, repeat)

    def __rshift__(self: Self, n: int) -> Self:
        return self.__class__(self.duration, self.repeats + n)

    def __lshift__(self: Self, n: int) -> Self:
        return self.__class__(self.duration, self.repeats - n)

    def __mul__(self: Self, delta: Duration | timedelta) -> Self:
        if isinstance(delta, timedelta):
            return self.__class__(self.duration.delta + delta, self.repeats)
        return self.__class__(self.duration.delta + delta.delta)

    def __truediv__(self: Self, delta: Duration | timedelta) -> Self:
        if isinstance(delta, timedelta):
            return self.__class__(self.duration.delta - delta, self.repeats)
        return self.__class__(self.duration.delta - delta.delta)

    def __getitem__(self: Self, i: int | slice) -> D_co | list[D_co]:
        if isinstance(i, slice):
            return [self.duration * n for n in range(i.start, i.stop, i.step)]
        return self.duration * i

    def __iter__(self: Self) -> Iterator[D_co]:
        if self.repeats is None:
            i = 0
            while True:
                yield self.duration * i
                i += 1
        else:
            for i in range(self.repeats + 1):
                yield self.duration * i

    @property
    def as_str(self: Self) -> str:
        r = "" if self.repeats is None else self.repeats
        return f"R{r}/{self.duration}"

    @property
    def _json_data(self: Self) -> JsonType:
        return {
            "duration": self.duration.as_str,
            "count": self.repeats
        }


@dataclass(slots=True, frozen=True, order=True)
class RepeatDuration(Model, Generic[D_co]):
    start: D_co
    end: D_co
    repeats: int | None
    duration_type: ClassVar[type[Duration]]

    @classmethod
    def interval_type(cls: type[Self]) -> type[D_co]:
        return typing.get_args(cls)[0]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        m = REPEAT_REGEX.fullmatch(s)
        repeat = int(m.group(1))
        start, end = m.group(2).split("--")
        return cls(start, end, repeat)

    def __rshift__(self: Self, n: int) -> Self:
        return self.__class__(self.start, self.end, self.repeats + n)

    def __lshift__(self: Self, n: int) -> Self:
        return self.__class__(self.start, self.end, self.repeats - n)

    def __mul__(self: Self, scale: float) -> Self:
        return self.__class__(self.start * scale, self.end.delta * scale, self.repeats)

    def __truediv__(self: Self, scale: float) -> Self:
        return self.__class__(self.start.delta / scale, self.end.delta / scale, self.repeats)

    def __floordiv__(self: Self, scale: float) -> Self:
        return self.__class__(self.start // scale, self.end // scale, self.repeats)

    def __add__(self: Self, delta: Duration | timedelta) -> Self:
        return self.__class__(self.start + delta, self.end + delta)

    def __sub__(self: Self, delta: Duration | timedelta) -> Self:
        return self.__class__(self.start - delta, self.end - delta)

    def __getitem__(self: Self, i: int | slice) -> D_co | list[tuple[D_co, D_co]]:
        if isinstance(i, slice):
            return [(self.start + self.end * n, self.end + self.end * n) for n in range(i.start, i.stop, i.step)]
        return [self.start + self.end * i, self.end + self.end * i]

    def __iter__(self: Self) -> Iterator[tuple[D_co, D_co]]:
        if self.repeats is None:
            i = 0
            while True:
                yield self.start + self.end * i, self.end + self.end * i
                i += 1
        else:
            for i in range(self.repeats + 1):
                yield self.start + self.end * i, self.end + self.end * i

    @property
    def as_str(self: Self) -> str:
        r = "" if self.repeats is None else self.repeats
        return f"R{r}/{self.start}--{self.end}"

    @property
    def duration(self: Self) -> Duration:
        return self.end - self.start

    @property
    def _json_data(self: Self) -> JsonType:
        return {
            "start": self.start.as_str,
            "end": self.end.as_str,
            "repeats": self.repeats
        }
