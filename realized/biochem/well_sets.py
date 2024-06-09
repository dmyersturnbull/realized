# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
import re
import typing
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from typing import Self, ClassVar, TypeVar, Generic

from pocketutils import KeyReusedError

from realized._core import Model, NullableInt, NULL_INT
from realized.biochem.wells import Well
from realized.errors import RealizedParseError

__all__ = ["WellSet"]
Coordinate = tuple[int, int]
CoordinatePair = tuple[Coordinate, Coordinate]
PATTERN = re.compile(r""" *([A-H]+[0-9]+) *(?:(-|\*|\.{3}) *([A-H]+[0-9]+))? *""")
W = TypeVar("W", bound=Well)


def simple_range(a: str, b: str, typ: type[Well]) -> Iterator[W]:
    ar, ac = typ.from_str(a).as_rc
    br, bc = typ.from_str(b).as_rc
    if ar == br:
        for c in range(ac, bc + 1):
            yield typ.from_rc(ar, c)
    elif ac == bc:
        for r in range(ar, br + 1):
            yield typ.from_rc(r, ac).as_rc
    msg = f"{a}-{b} is not a simple range"
    raise RealizedParseError(msg)


def block_range(a: str, b: str, typ: type[Well]) -> Iterator[W]:
    ar, ac = typ.from_str(a).as_rc
    br, bc = typ.from_str(b).as_rc
    for r in range(ar, br + 1):
        for c in range(ac, bc + 1):
            yield typ.from_rc(r, c)


def traversal_range(a: str, b: str, typ: type[Well]) -> Iterator[W]:
    ai = typ.from_str(a).as_index
    bi = typ.from_str(b).as_index
    for i in range(ai, bi + 1):
        yield typ.from_index(i)


@dataclass(slots=True, frozen=True, order=True, init=False)
class WellSet(Model, Generic[W], metaclass=abc.ABCMeta):

    _original: list[W]
    _sorted: list[W] = field(init=False)
    _n_rows: ClassVar[int]
    _n_cols: ClassVar[int]

    def __init__(self: Self, wells: Sequence[W]) -> None:
        delta = set(self._original).symmetric_difference(set(wells))
        if len(delta) > 0:
            raise KeyReusedError(
                f"Well range contains duplicate wells {delta}",
                keys=frozenset([str(w) for w in delta])
            )
        self._sorted = list(sorted(wells))

    @classmethod
    def well_type(cls: type[Self]) -> type[W]:
        return typing.get_args(cls)[0]

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        """
        Returns the labels from the expression, inclusive.
        Examples:
            A01-A10   (sequence in a single row)
            A01-E01   (sequence in a single column)
            A01*C01   (a rectangular block)
            A01...C01 (a traversal of the wells in order)
        """
        wells = []
        for txt in v.split(","):
            try:
                wells += cls._parse(txt)
            except RealizedParseError as e:
                raise RealizedParseError(f"'{txt}' is not a valid well expression", value=v) from e
        return cls(wells)

    def __bool__(self: Self) -> bool:
        return not self.is_empty

    def __len__(self: Self) -> int:
        return len(self._original)

    def __iter__(self: Self) -> Iterator[W]:
        return iter(self._original)

    @property
    def as_str(self: Self) -> str:
        wells: Self = self._sorted
        if self.is_empty:
            return ""
        if self.as_single:
            return wells[0].as_str
        if self.as_row or self.as_col:
            return f"{wells[0]}-{wells[-1]}"
        if self.as_block:
            return f"{wells[0]}*{wells[-1]}"
        if self.as_sequence:
            return f"{wells[0]}...{wells[-1]}"
        return ",".join(wells)

    @property
    def wells(self: Self) -> Sequence[W]:
        return list(self._original)

    @property
    def sorted(self: Self) -> Self:
        return self.__class__(self._sorted, self._sorted)

    @property
    def is_empty(self: Self) -> bool:
        return len(self._sorted) == 0

    @property
    def as_single(self: Self) -> Coordinate | None:
        if len(self._sorted) == 1:
            return self._sorted[0].as_rc
        return None

    @property
    def as_row(self: Self) -> NullableInt:
        w0 = None
        for w in self._sorted:
            if w0 is not None and w.row != w0.row:
                return NULL_INT
            if w0 is not None and w.col != w0.col + 1:
                return NULL_INT
            w0 = w
        return NullableInt.of(w0.row)

    @property
    def as_col(self: Self) -> NullableInt:
        w0 = None
        for w in self._sorted:
            if w0 is not None and w.col != w0.col:
                return NULL_INT
            if w0 is not None and w.row != w0.row + 1:
                return NULL_INT
            w0 = w
        return NullableInt.of(w0.col)

    @property
    def as_sequence(self: Self) -> CoordinatePair | None:
        w00 = (-1, -1)
        w0 = None
        for w in self._sorted:
            if w0 is None:
                w00 = w.as_rc
            if w0 is not None and w.as_index != w0.index + 1:
                return None
            w0 = w
        return w00, w0.as_rc

    @property
    def as_block(self: Self) -> CoordinatePair | None:
        wells = self._sorted
        w00 = wells[0].row
        w01 = wells[-1].row
        w10 = wells[0].col
        w11 = wells[-1].col
        if len(wells) != (w01 - w00) * (w11 - w10):
            return None
        actual: set[tuple[int, int]] = {(w.row, w.col) for w in wells}
        for r in range(w00, w01 + 1):
            for c in range(w10, w11 + 1):
                if (r, c) not in actual:
                    return None
        return wells[0].as_rc, wells[-1].as_rc

    @classmethod
    def _parse(cls: type[Self], v: str) -> Iterator[W]:
        match = PATTERN.fullmatch(v)
        if match is None:
            msg = f"'{v}' is not a valid well expression"
            raise RealizedParseError(msg, value=v)
        a, x, b = match.group(1), match.group(2), match.group(3)
        if x is None:
            return cls.well_type.from_str(a)
        elif x == "-":
            return simple_range(a, b, cls.well_type)
        elif x == "*":
            return block_range(a, b, cls.well_type)
        elif x == "...":
            return traversal_range(a, b, cls.well_type)
        msg = f"'{x}' is not a valid range operator"
        raise RealizedParseError(msg, value=v)
