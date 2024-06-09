# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

import abc
from collections import namedtuple
from dataclasses import dataclass
from typing import ClassVar, Self, Any, TypeVar
from weakref import WeakValueDictionary

from realized.biochem.wells import Well
from realized.biochem.well_sets import WellSet

__all__ = [
    "WellTypeAndWellSetType",
    "AbstractWellTypeFactory",
    "DefaultWellTypeFactory",
    "WellTypeRegistry",
    "WELL_TYPES",
]
V_co = TypeVar("V_co", covariant=True)


class WellTypeAndWellSetType(namedtuple):
    well: type[Well]
    well_set: type[WellSet]


@dataclass(slots=True, frozen=True)
class AbstractWellTypeFactory(metaclass=abc.ABCMeta):

    def well_type(self: Self, rows: int, cols: int) -> type[Well]:
        return self.create_types(rows, cols).well

    def well_set_type(self: Self, rows: int, cols: int) -> type[WellSet]:
        return self.create_types(rows, cols).well_set

    def create_types(self: Self, rows: int, cols: int) -> WellTypeAndWellSetType:
        raise NotImplementedError()


@dataclass(slots=True, frozen=True)
class DefaultWellTypeFactory(AbstractWellTypeFactory):

    def create_types(self: Self, rows: int, cols: int) -> WellTypeAndWellSetType:
        @dataclass(slots=True, frozen=True, order=True)
        class _Well(Well):
            _n_rows: ClassVar[int] = rows
            _n_cols: ClassVar[int] = cols

        _Well.__name__ = f"{Well.__name__}{rows}x{cols}"

        @dataclass(slots=True, frozen=True, order=True)
        class _WellSet(WellSet[_Well]):
            _n_rows: ClassVar[int] = rows
            _n_cols: ClassVar[int] = cols

        _WellSet.__name__ = f"{WellSet.__name__}{rows}x{cols}"

        return WellTypeAndWellSetType(_Well, _WellSet)


@dataclass(slots=True, frozen=True)
class WellTypeRegistry(AbstractWellTypeFactory):

    cache: WeakValueDictionary[tuple[int, int], WellTypeAndWellSetType]
    underlying: AbstractWellTypeFactory

    @classmethod
    def new_empty(cls: type[Self], underlying: AbstractWellTypeFactory) -> Self:
        return WellTypeRegistry(WeakValueDictionary({}), underlying)

    def __eq__(self: Self, other: Any) -> bool:
        if not isinstance(other, WellTypeRegistry):
            return False
        return set(self.cache.keys()) == set(other.cache.keys())

    def register(self: Self, *types: tuple[int, int]) -> None:
        for r, c in types:
            self.cache[(r, c)] = self.underlying.create_types(r, c)

    def create_types(self: Self, rows: int, cols: int) -> WellTypeAndWellSetType:
        if (rows, cols) not in self.cache:
            self.register((rows, cols))
        return self.cache[(rows, cols)]


DEFAULT_TYPES = [
    (2, 3),
    (3, 4),
    (4, 6),
    (6, 8),
    (8, 12),
    (16, 24),
    (32, 48),
    (48, 72),
]
_FACTORY = DefaultWellTypeFactory()
WELL_TYPES = WellTypeRegistry.new_empty(_FACTORY)
WELL_TYPES.register(*DEFAULT_TYPES)
