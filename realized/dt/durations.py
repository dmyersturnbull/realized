# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import functools
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Self

from pocketutils import ValueIllegalError

from realized._core import Model
from realized.errors import RealizedParseError

__all__ = ["Duration", "IsoDuration", "ColonSeparatedDuration", "Hmsu"]
DURATION_MICROSEC_REGEX = re.compile(
    r"PT"
    r"(?:(?P<hours>[1-9]|1[0-9]|2[0-3])H)??"
    r"(?:(?P<minutes>[1-9]|[1-5][0-9])M)??"
    r"(?:(?P<seconds>[1-9]|[1-5][0-9])S)??"
    r"(?:\.(?P<microseconds>\d{1,6})?S)??"
)
DURATION_HMSU_REGEX = re.compile(
    r"(?P<hours>\d+)"
    r":(?P<minutes>[0-5]\d|60)"
    r":(?P<seconds>[0-5]\d|60)"
    r"(?:\.(?P<microseconds>\d{3}|\d{6}))?"
)


@functools.total_ordering
@dataclass(slots=True, frozen=True)
class Hmsu:
    """
    A tuple of hour, minute, second, and microsecond.
    """

    sign: int
    h: int
    m: int
    s: int
    u: int

    def __lt__(self: Self, other: Self) -> bool:
        if self.__class__ != other.__class__:
            msg = f"Cannot compare {self.__class__.__qualname__} to {other.__class__.__qualname__}"
            raise TypeError(msg)
        return any(
            getattr(self, k) < 0 and self.sign * getattr(self, k) < other.sign * getattr(other, k)
            for k in ("h", "m", "s", "u")
        )

    def __le__(self: Self, other: Self) -> bool:
        if self.__class__ != other.__class__:
            msg = f"Cannot compare {self.__class__.__qualname__} to {other.__class__.__qualname__}"
            raise TypeError(msg)
        return any(
            getattr(self, k) <= 0 and self.sign * getattr(self, k) < other.sign * getattr(other, k)
            for k in ("h", "m", "s", "u")
        )


@dataclass(slots=True, frozen=True, order=True)
class Duration:
    """
    An amount of time.
    This can be the difference between two instants in time or an amount of elapsed time.
    These two concepts should not be confused.

    - As a difference between two instants: This includes clock updates and timezone changes.
      It can be calculated by subtracting two datetimes (local or zoned),
      or by comparing two values from a non-monotonic system clock.
    - As an elapsed duration: This excludes clock updates and timezone changes.
      It can be calculated by comparing two values from a monotonic clock,
      or by subtracting two NTP times.
    """

    delta: timedelta

    def __post_init__(self: Self) -> None:
        if self.delta.days < 0 and self.delta == timedelta(0):
            raise ValueIllegalError("Duration is negative 0", value=-0.0)

    def __truediv__(self: Self, v: float | Self | timedelta) -> Self:
        v = v.delta if isinstance(v, Duration) else v
        return self.__class__(self.delta / v)

    def __floordiv__(self: Self, v: float | Self | timedelta) -> Self:
        v = v.delta if isinstance(v, Duration) else v
        return self.__class__(self.delta // v)

    def __add__(self: Self, v: Self | timedelta) -> Self:
        v = v.delta if isinstance(v, Duration) else v
        return self.delta + v

    def __sub__(self: Self, v: Self | timedelta) -> Self:
        v = v.delta if isinstance(v, Duration) else v
        return self.delta - v

    def __abs__(self: Self) -> Self:
        return self.__class__(abs(self.delta))

    @classmethod
    def from_any(cls: type[Self], v: str) -> Self:
        for fn in (cls.from_iso8601, cls.from_colon_separated):
            try:
                return fn(v)
            except RealizedParseError:
                pass
        msg = f"'{v}' is in neither ISO8601 nor colon-separated format"
        raise RealizedParseError(msg)

    @classmethod
    def from_iso8601(cls: type[Self], v: str) -> Self:
        match = DURATION_MICROSEC_REGEX.fullmatch(v)
        if match is None:
            msg = f"'{v}' is not in ISO8601 format"
            raise RealizedParseError(msg, value=v)
        delta = timedelta(**{k: int(v) for k, v in match.groupdict().items()})
        return cls(delta)

    @classmethod
    def from_colon_separated(cls: type[Self], v: str) -> Self:
        match = DURATION_HMSU_REGEX.fullmatch(v)
        if not match:
            msg = f"'{v} is not in HH:MM:SS[.iiiiii] format"
            raise RealizedParseError(msg)
        return Hmsu(
            sign=1,
            h=int(match.group(1)),
            m=int(match.group(2)),
            s=int(match.group(3)),
            u=int(match.group(4)),
        )

    @classmethod
    def from_seconds(cls: type[Self], v: int) -> Self:
        return cls(timedelta(seconds=v))

    @classmethod
    def from_microseconds(cls: type[Self], v: int) -> Self:
        return cls(timedelta(microseconds=v))

    @property
    def as_seconds(self: Self) -> int:
        return int(self.delta.total_seconds())

    @property
    def as_microseconds(self: Self) -> int:
        # always exact
        return int(1000000 * self.delta.total_seconds())

    @property
    def as_iso8601(self: Self) -> str:
        x = self.as_hmsu
        return (
            "PT"
            + (f"{x.h}H" if x.h > 0 else "")
            + (f"{x.m}M" if x.m > 0 else "")
            + (f"{x.s}S" if x.s > 0 and x.u == 0 else "")
            + (f"{x.s}.{x.u}S" if x.u > 0 else "")
        )

    @property
    def as_colon_separated(self: Self) -> str:
        x = self.as_hmsu
        h = f"{x.h:02}" if len(str(x.h)) < 2 else str(x.h)
        if x.u > 0:
            return f"{h}:{x.m:02}:{x.s:02}.{x.u}"
        return f"{h}:{x.m:02}:{x.s:02}"

    @property
    def as_hmsu(self: Self) -> Hmsu:
        mag = abs(self.delta)
        seconds = 24 * 3600 * mag.days + mag.seconds
        return Hmsu(
            sign=self.sign,
            h=seconds // 3600,
            m=seconds % 3600 // 60,
            s=seconds % 60,
            u=mag.microseconds,
        )

    @property
    def sign(self: Self) -> int:
        return -1 if self.delta.days < 0 else 1  # that's how timedelta works


@dataclass(slots=True, frozen=True, order=True)
class IsoDuration(Duration, Model):

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        return cls.from_iso8601(v)

    @property
    def as_str(self: Self) -> str:
        return self.as_iso8601


@dataclass(slots=True, frozen=True, order=True)
class ColonSeparatedDuration(Duration, Model):

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        return cls.from_colon_separated(v)

    @property
    def as_str(self: Self) -> str:
        return self.as_colon_separated
