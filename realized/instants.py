from __future__ import annotations

import abc
from abc import ABCMeta
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Self
from zoneinfo import ZoneInfo

import regex

from realized._core import Model

PERIOD_REGEX = regex.compile(
    r"^P(?:(\d+)D)??T(?:(\d+)H)??(?:(\d+)M)??(?:(\d+)(?:\.(\d{1,6}))?S)??$", flags=regex.V1
)


@dataclass(slots=True, frozen=True, order=True)
class Duration(Model):
    td: timedelta

    def __mul__(self, v: float) -> Self:
        return Duration(self.td * v)

    def __truediv__(self, v: float) -> Self:
        return Duration(self.td / v)

    def __add__(self, v: Duration) -> Self:
        return self.td + v.td

    def __sub__(self, v: Duration) -> Self:
        return self.td - v.td

    @classmethod
    def parse(cls, v: str) -> Self:
        match = PERIOD_REGEX.fullmatch(v)
        if match is None:
            raise ValueError(v)
        d, h, m, s, u = [int(x) for x in match.groups()]
        return Duration(timedelta(days=d, hours=h, minutes=m, seconds=s, microseconds=u))

    @classmethod
    def from_microseconds(cls, v: int) -> Self:
        return Duration(timedelta(microseconds=v))

    def to_microseconds(self) -> int:
        # always exact
        return int(1000 * self.td.total_seconds())

    def __post_init__(self):
        super().__post_init__()
        if self.td.total_seconds() < 0:
            raise ValueError(f"Duration {self.td} is negative")

    def hms(self) -> str:
        s_tot = self.td.total_seconds()
        h, m, s = s_tot // 3600, s_tot // 60, s_tot % 60
        return f"{h:02}:{m:02}:{s:02}"

    def str(self) -> str:
        s_tot = self.td.seconds
        d = self.td.days
        h, m, s = s_tot // 3600, s_tot // 60, s_tot % 60
        u = self.td.microseconds
        return "".join(
            (
                f"P{d}T" if d > 0 else "PT",
                f"{h}H" if h > 0 else "",
                f"{m}M" if m > 0 else "",
                f"{s}S" if s > 0 or u > 0 else "",
                f"{u}" if u > 0 else "",
            )
        )


@dataclass(slots=True, frozen=True, order=True)
class _Instant(Model):
    dt: datetime

    def __post_init__(self):
        super().__post_init__()
        if self.dt.tzinfo is None or not isinstance(self.dt.tzinfo, ZoneInfo):
            raise ValueError(f"Non-zoned {self}")

    @property
    def zone_info(self) -> ZoneInfo:
        # noinspection PyTypeChecker
        return self.dt.tzinfo

    @property
    def zone_name(self) -> str:
        return self.dt.tzinfo.tzname(self.dt).replace("UTC", "Etc/UTC")

    @property
    def offset(self) -> timedelta:
        return self.dt.utcoffset()

    @property
    def offset_str(self) -> str:
        f = self.dt.utcoffset().total_seconds()
        if f % 60 != 0 or abs(f) > 14 * 3600:
            raise ValueError(str(f))
        return "-" if f < 0 else "+" + f"{abs(f)//3600:02}:{abs(f)//60:02}"

    def str(self) -> str:
        raise NotImplementedError()


@dataclass(slots=True, frozen=True, order=True)
class _OffsetInstant(_Instant, metaclass=ABCMeta):
    @classmethod
    def parse(cls, s: str) -> Self:
        return cls(datetime.fromisoformat(s.replace("−", "-")))

    def compact(self) -> str:
        s0, s1 = self[:-5], self[-5:]
        s0 = s0.replace("-", "").replace(":", "")
        return s0 + s1


@dataclass(slots=True, frozen=True, order=True)
class OffsetInstantSecond(_OffsetInstant):
    def str(self) -> str:
        return self.dt.isoformat(timespec="second")


@dataclass(slots=True, frozen=True, order=True)
class OffsetInstantMicrosecond(_OffsetInstant):
    def str(self) -> str:
        return self.dt.isoformat(timespec="microsecond")


@dataclass(slots=True, frozen=True, order=True)
class _CityInstant(_Instant):
    @classmethod
    def parse(cls, s: str) -> Self:
        s0, s1 = s.split(" ")
        zi = ZoneInfo(s1.replace("Etc/UTC", "UTC"))
        dt = datetime.fromisoformat(s0.replace("−", "-"))
        if dt.tzinfo.utcoffset(dt) != zi.utcoffset(dt):
            raise ValueError(f"Mismatch offset for {dt} and {zi}")
        return cls(dt.replace(tzinfo=zi))

    def str(self) -> str:
        s01 = self.dt.isoformat(timespec="second")
        return s01 + " [" + self.zone_name + "]"

    def compact(self) -> str:
        s01 = self.dt.isoformat(timespec="second")
        s0, s1 = s01[:-5], s01[-5:]
        s0 = s0.replace("-", "").replace(":", "")
        return s0 + s1 + " [" + self.zone_name + "]"


@dataclass(slots=True, frozen=True, order=True)
class _UtcInstant(_Instant, metaclass=abc.ABCMeta):
    def __add__(self, v: Duration) -> Self:
        return self.__class__.__init__(self.dt + v.td)

    def __sub__(self, v: Duration) -> Self:
        return self.__class__.__init__(self.dt - v.td)

    @classmethod
    def parse(cls, s: str) -> Self:
        return cls(datetime.fromisoformat(s.replace("−", "-").replace("Z", "+00:00")))

    def __post_init__(self):
        super().__post_init__()
        if self.zone_name != "UTC":
            raise ValueError(f"Non-UTC {self}")


@dataclass(slots=True, frozen=True, order=True)
class UtcInstantSecond(_UtcInstant):
    def str(self) -> str:
        return self.dt.isoformat(timespec="second").replace("+00:00", "Z")

    def compact(self) -> str:
        return repr(self).replace("-", "").replace(":", "")


@dataclass(slots=True, frozen=True, order=True)
class UtcInstantMicrosecond(_UtcInstant):
    def str(self) -> str:
        return self.dt.isoformat(timespec="microsecond").replace("+00:00", "Z")
