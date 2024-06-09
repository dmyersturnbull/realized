# SPDX-FileCopyrightText: Copyright 2021-2023, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0
"""
Exception classes for suretime.

Model and utility classes for suretime.
"""

from typing import Self, Unpack, Any

from pocketutils import Error

__all__ = [
    "DatetimeMissingZoneError",
    "ZoneMismatchError",
    "RealizedParseError",
]


class DatetimeMissingZoneError(Error):
    """
    Raised when a datetime lacks a required zone.
    """


class ZoneMismatchError(Error):
    """
    Raised when two zones needed to match.
    """


class RealizedParseError(Error):
    """
    Raised on failure to parse a format.
    """

    def __init__(
        self: Self,
        message: str | None = None,
        *,
        value: Any = None,
        **kwargs: Unpack[str, Any]
    ) -> None:
        super().__init__(message, value=value, **kwargs)
        self.value = value
