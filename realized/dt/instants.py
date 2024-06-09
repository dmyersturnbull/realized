# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Self
from zoneinfo import ZoneInfo

from realized import Resolution
from realized._core import Model, JsonType
from realized.dt.durations import Duration
from realized.errors import DatetimeMissingZoneError, ZoneMismatchError

__all__ = ["Instant", "InstantUtc", "InstantWithOffset", "InstantWithCity"]


@dataclass(slots=True, frozen=True, order=True)
class Instant:
    """
    An instant in time with either second or microsecond resolution.
    Must be zoned with a UTC offset or an IANA timezone name.
    """

    dt: datetime

    def __post_init__(self: Self) -> None:
        if self.dt.tzinfo is None or not isinstance(self.dt.tzinfo, ZoneInfo):
            raise DatetimeMissingZoneError(f"Non-zoned {self}")
        f = self.dt.utcoffset().total_seconds()
        if f % 60 != 0 or abs(f) > 14 * 3600:
            raise AssertionError(str(f))

    def __add__(self: Self, delta: Duration | timedelta) -> Self:
        if isinstance(delta, timedelta):
            return self.__class__(self.dt + delta)
        return self.__class__(self.dt + delta.delta)

    def __sub__(self: Self, delta: Duration | timedelta) -> Self:
        if isinstance(delta, timedelta):
            return self.__class__(self.dt - delta)
        return self.__class__(self.dt - delta.delta)

    @property
    def as_rfc3339(self: Self) -> str:
        return self.to_rfc3339(Resolution.default())

    def to_rfc3339(self: Self, min_resolution: Resolution) -> str:
        return self.dt.isoformat(timespec=min_resolution)

    @property
    def ctime_utc(self: Self) -> str:
        # noinspection PyTypeChecker
        return self.dt.astimezone(ZoneInfo("Etc/UTC")).ctime()

    @property
    def zone(self: Self) -> ZoneInfo:
        # noinspection PyTypeChecker
        return self.dt.tzinfo

    @property
    def offset(self: Self) -> timedelta:
        return self.dt.utcoffset()

    @property
    def offset_str(self: Self) -> str:
        f = self.dt.utcoffset().total_seconds()
        return "-" if f < 0 else "+" + f"{abs(f)//3600:02}:{abs(f)//60:02}"

    @property
    def _raw_timestamp(self: Self) -> str:
        return self.dt.isoformat(timespec=Resolution.default())


@dataclass(slots=True, frozen=True, order=True)
class InstantUtc(Instant, Model):

    def __post_init__(self: Self) -> None:
        super().__post_init__()
        if self.zone_name != "Etc/UTC":
            raise ZoneMismatchError(f"Zone '{self}' is not Etc/UTC")

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        s = s.replace("−", "-").replace("Z", "+00:00")
        return cls(datetime.fromisoformat(s))

    @property
    def as_str(self: Self) -> str:
        return self._raw_timestamp.replace("+00:00", "Z")

    @property
    def as_compact_str(self: Self) -> str:
        return self._raw_timestamp.replace("+00:00", "Z").replace("-", "").replace(":", "")


@dataclass(slots=True, frozen=True, order=True)
class InstantWithOffset(Instant, Model):

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        return cls(datetime.fromisoformat(s.replace("−", "-")))

    @property
    def as_str(self: Self) -> str:
        return self.as_rfc3339

    @property
    def as_compact_str(self: Self) -> str:
        s0, s1 = self._raw_timestamp[:-5], self._raw_timestamp[-5:]
        s0 = s0.replace("-", "").replace(":", "")
        return s0 + s1


@dataclass(slots=True, frozen=True, order=True)
class InstantWithCity(Instant, Model):

    def __post_init__(self: Self) -> None:
        super().__post_init__()
        if self.dt.tzinfo.tzname(self.dt) is None:
            raise DatetimeMissingZoneError(f"{self.dt} has zone {self.dt.tzinfo} with no name")

    @classmethod
    def from_str(cls: type[Self], s: str) -> Self:
        s0, s1 = s.split(" ")
        zi = ZoneInfo(s1.replace("UTC", "Etc/UTC").strip_suffix("]").strip_prefix("["))
        dt = datetime.fromisoformat(s0.replace("−", "-"))
        if dt.tzinfo.utcoffset(dt) != zi.utcoffset(dt):
            raise ZoneMismatchError(f"Mismatch offset for {dt} and {zi}")
        return cls(dt.replace(tzinfo=zi))

    @property
    def as_str(self: Self) -> str:
        return self._raw_timestamp + " [" + self.zone_name + "]"

    @property
    def as_compact_str(self: Self) -> str:
        s0, s1 = self._raw_timestamp[:-5], self._raw_timestamp[-5:]
        s0 = s0.replace("-", "").replace(":", "")
        return f"{s0}{s1} [{self.zone_name}]"

    @property
    def zone_name(self: Self) -> str:
        return self.dt.tzinfo.tzname(self.dt).replace("UTC", "Etc/UTC")

    @property
    def _json_data(self: Self) -> JsonType:
        return {
            "timestamp": self._raw_timestamp,
            "timezone": self.zone_name
        }
