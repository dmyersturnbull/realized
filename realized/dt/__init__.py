# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

import enum
from typing import Self

__all__ = ["Resolution", "DEFAULT_MIN_RESOLUTION"]


class Resolution(enum.StrEnum):
    SECOND: Self = "second"
    MILLISECOND: Self = "millisecond"
    MICROSECOND: Self = "microsecond"

    @classmethod
    def default(cls: type[Self]) -> Self:
        return Resolution.SECOND

    @property
    def abbrev(self: Self) -> str:
        return {Resolution.SECOND: "s", Resolution.MILLISECOND: "ms", Resolution.MICROSECOND: "us"}[self]

    @property
    def decimals(self: Self) -> int:
        return {Resolution.SECOND: 0, Resolution.MILLISECOND: 3, Resolution.MICROSECOND: 6}[self]


DEFAULT_MIN_RESOLUTION = Resolution.SECOND

"""

INSTANT_UTC_MICROSEC_REGEX = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"\.(?P<microsecond>\d{6})"
    r"Z"
)
INSTANT_OFFSET_MICROSEC_REGEX = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"\.(?P<microsecond>\d{6})"
    r"(?P<offset_sign>[+-])(?P<offset_hour>\d{2}):(?P<offset_minute>\d{2})",
)
INSTANT_CITY_MICROSEC_REGEX = re.compile(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"\.(?P<microsecond>\d{6})Z"
    r"(?P<offset_sign>[+-])(?P<offset_hour>\d{2}):(?P<offset_minute>\d{2})"
    r" \[(?P<city>[A-Za-z]+/[A-Za-z_0-9]+)\]"
)
"""
