# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from dataclasses import dataclass
from typing import Self, TYPE_CHECKING, Unpack, Any

if TYPE_CHECKING:
    from pint import UnitRegistry, Quantity, Unit

from realized._core import JsonType, Model

__all__ = ["Dimensioned"]


class LazyUnitRegistry:

    ureg: UnitRegistry | None
    Q: Quantity | None

    def __call__(self: Self, *args: Any, **kwargs: Unpack[Mapping[str, Any]]):
        if self.Q is None:
            self.ureg = UnitRegistry(non_int_type=Decimal)
            self.Q = self.ureg.Quantity
            self.Q.separate_format_defaults = True
        return self.Q(*args, **kwargs)


UNIT_REGISTRY = LazyUnitRegistry()


@dataclass(slots=True, frozen=True, order=True)
class Dimensioned(Model):

    quantity: Quantity

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        return cls(UNIT_REGISTRY(v))

    def __add__(self: Self, other: Quantity) -> Self:
        return self.__class__(self.quantity + other)

    def __sub__(self: Self, other: Quantity) -> Self:
        return self.__class__(self.quantity - other)

    def __mul__(self: Self, other: float | Decimal | Quantity | Unit) -> Self:
        return self.__class__(self.quantity * other)

    def __truediv__(self: Self, other: float | Decimal | Quantity | Unit) -> Self:
        return self.__class__(self.quantity / other)

    def __round__(self: Self, n: int | None = None) -> Self:
        return self.__class__(round(self.quantity, n))

    def round(self: Self, n: int | None = None) -> Self:
        return round(self, n)

    def to_base_units(self: Self) -> Self:
        return self.__class__(self.quantity.to_base_units())

    def to_reduced_units(self: Self) -> Self:
        return self.__class__(self.quantity.to_reduced_units())

    @property
    def as_str(self: Self) -> str:
        return str(self.quantity)

    @property
    def as_simple_str(self: Self) -> str:
        return f"{self.quantity:~P}"

    @property
    def units(self: Self) -> str:
        return self.quantity.units

    @property
    def magnitude(self: Self) -> Decimal:
        return self.quantity.magnitude

    @property
    def _json_data(self: Self) -> JsonType:
        return {
            "magnitude": str(self.magnitude),
            "units": str(self.units)
        }
