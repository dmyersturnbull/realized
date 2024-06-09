# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
import math
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

from realized._core import Model

RECTANGLE_XY_REGEX = re.compile(r"\((?P<left>\d+),(?P<top>\d+)\)x\((?P<right>\d+),(?P<bottom>\d+)\)")
SCALE_XY_REGEX = re.compile(r"\((?P<x>\d+),(?P<y>\d+)\)")


@dataclass(slots=True, frozen=True, order=True)
class XY(Model):

    x: Decimal
    y: Decimal

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        match = SCALE_XY_REGEX.fullmatch(v)
        return cls(**{k: Decimal(i) for k, i in match.groupdict().items()})

    def __mul__(self: Self, other: Decimal | float | Self) -> Self:
        if isinstance(other, (Decimal, float)):
            other = self.__class__(other, other)
        return self.__class__(self.x * other.x, self.y * other.y)

    def __truediv__(self: Self, other: Decimal | float | Self) -> Self:
        if isinstance(other, (Decimal, float)):
            other = self.__class__(other, other)
        return self.__class__(self.x / other.x, self.y / other.y)

    def __add__(self: Self, other: Decimal | float | Self) -> Self:
        if isinstance(other, (Decimal, float)):
            other = self.__class__(other, other)
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self: Self, other: Decimal | float | Self) -> Self:
        if isinstance(other, (Decimal, float)):
            other = self.__class__(other, other)
        return self.__class__(self.x - other.x, self.y - other.y)

    @property
    def as_str(self: Self) -> str:
        return f"({self.x},{self.y})"


@dataclass(slots=True, frozen=True, order=True)
class Rectangle(Model, metaclass=abc.ABCMeta):

    left: Decimal
    top: Decimal
    right: Decimal
    bottom: Decimal

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        match = RECTANGLE_XY_REGEX.fullmatch(v)
        return cls(**{k: Decimal(i) for k, i in match.groupdict().items()})

    def __rshift__(self: Self, other: Decimal | float | XY) -> Self:
        if isinstance(other, (Decimal, float)):
            other = XY(other, other)
        return self.__class__(
            self.left + other.x,
            self.top + other.y,
            self.right - other.x,
            self.bottom - other.y,
        )

    def __lshift__(self: Self, other: Decimal | float | XY) -> Self:
        if isinstance(other, (Decimal, float)):
            other = XY(other, other)
        return self.__class__(
            self.left - other.x,
            self.top - other.y,
            self.right + other.x,
            self.bottom + other.y,
        )

    def __mul__(self: Self, other: Decimal | float | XY) -> Self:
        if isinstance(other, (Decimal, float)):
            other = XY(other, other)
        return self.__class__(
            self.left * other.x,
            self.top * other.y,
            self.right * other.x,
            self.bottom * other.y,
        )

    def __truediv__(self: Self, other: Decimal | float | XY) -> Self:
        if isinstance(other, (Decimal, float)):
            other = XY(other, other)
        return self.__class__(
            self.left / other.x,
            self.top / other.y,
            self.right / other.x,
            self.bottom / other.y,
        )

    def __add__(self: Self, other: Self | XY) -> Self:
        if isinstance(other, XY):
            other = self.__class__(other.y, other.x, other.y, other.x)
        return self.__class__(
            self.left + other.left,
            self.top + other.top,
            self.right + other.right,
            self.bottom + other.bottom,
        )

    def __sub__(self: Self, other: Self | XY) -> Self:
        if isinstance(other, XY):
            other = self.__class__(other.y, other.x, other.y, other.x)
        return self.__class__(
            self.left - other.left,
            self.top - other.top,
            self.right - other.right,
            self.bottom - other.bottom,
        )

    def __round__(self: Self, n: int | None = None) -> Self:
        return self.__class__(
            round(self.left, n),
            round(self.top, n),
            round(self.right, n),
            round(self.bottom, n),
        )

    def round(self: Self, n: int | None = None) -> Self:
        return round(self, n)

    @property
    def as_str(self: Self) -> str:
        return f"({self.left},{self.top})x({self.right},{self.bottom})"

    @property
    def center(self: Self) -> XY:
        return XY(self.left + self.width / 2, self.top + self.height / 2)

    @property
    def width(self: Self) -> Decimal:
        return self.bottom - self.top

    @property
    def height(self: Self) -> Decimal:
        return self.bottom - self.top

    @property
    def area(self: Self) -> Decimal:
        return (self.right - self.left) * (self.bottom - self.top)

    def rotate(self: Self, rad: float) -> Self:
        sin = math.sin(rad)
        cos = math.cos(rad)
        y_prime = self.center.x * sin + self.center.y * cos
        x_prime = self.center.x * cos - self.center.y * sin
        return (
            x_prime + self.left,
            y_prime + self.top,
            x_prime + self.right,
            y_prime + self.bottom,
        )
