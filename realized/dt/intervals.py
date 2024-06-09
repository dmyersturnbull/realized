# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

import typing
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Generic, Self, TypeVar
from zoneinfo import ZoneInfo

from realized._core import Model
from realized.dt.instants import Instant
from realized.dt.durations import Duration
from realized.errors import ZoneMismatchError

__all__ = ["Interval"]
I_co = TypeVar("I_co", bound=Instant, covariant=True)


@dataclass(slots=True, frozen=True, order=True)
class Interval(Model, Generic[I_co]):
    """
    A start instant and an end instant with either second or microsecond resolution.
    """

    start: I_co
    end: I_co

    @classmethod
    def instant_type(cls: type[Self]) -> type[I_co]:
        return typing.get_args(cls)[0]

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        s1, s2 = s.split("--")
        return cls(cls.instant_type().from_str(s1), cls.instant_type().from_str(s2))

    def __post_init__(self: Self) -> None:
        if self.start.zone != self.end.zone:
            msg = f"Start zone {self.start.zone} and end zone {self.end.zone} differ"
            raise ZoneMismatchError(msg)

    def __add__(self: Self, delta: Duration | timedelta) -> Self:
        return self.__class__(self.start + delta, self.end + delta)

    def __sub__(self: Self, delta: Duration | timedelta) -> Self:
        return self.__class__(self.start - delta, self.end - delta)

    @property
    def as_str(self: Self) -> str:
        return self.start.to_str + "--" + self.end.to_str

    @property
    def duration(self: Self) -> Duration:
        return Duration(self.delta)

    @property
    def delta(self: Self) -> timedelta:
        return self.end.dt.astimezone(ZoneInfo("Etc/UTC")) - self.start.dt.astimezone(ZoneInfo("Etc/UTC"))

    def convert_to_zone(self: Self, zone: ZoneInfo | str) -> Self:
        if isinstance(zone, str):
            zone = ZoneInfo(zone)
        start = self.start.dt.astimezone(zone)
        end = self.end.dt.astimezone(zone)
        instance_type = self.instant_type()
        return self.__class__(instance_type.from_dt(start), instance_type.from_dt(end))

    @property
    def _json_data(self: Self) -> Any:
        return {
            "start": self.start.as_str,
            "end": self.end.as_str
        }
