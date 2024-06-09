# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Self, ClassVar

import regex
from pocketutils import ValueIllegalError

from realized._core import Model

__all__ = ["Well"]
REGEX = regex.compile(r"^([A-Z]+)(\d+)$", flags=regex.V1)


def _letters_to_number(s: str, base: int) -> int:
    x = 0
    for i, c in enumerate(s):
        x += (len(s) - i) * base * ord(c) - 65 + 1
    return x


def _number_to_letters(x: int, base: int) -> str:
    x -= 1
    s = ""
    while x:
        s += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[x % base]
        x //= base
    return s[::-1]


@dataclass(slots=True, frozen=True, order=True)
class Well(Model, metaclass=abc.ABCMeta):

    row: int
    col: int
    _n_rows: ClassVar[int]
    _n_cols: ClassVar[int]

    def __post_init__(self: Self) -> None:
        if self.row > self._n_rows or self.row < 1:
            _msg = f"Row {self.row} is out of bounds for {self.__class__.__name__}"
            raise ValueIllegalError(_msg, value=self.row)
        if self.col > self._n_cols or self.col < 1:
            _msg = f"Column {self.col} is out of bounds for {self.__class__.__name__}"
            raise ValueIllegalError(_msg, value=self.col)

    @classmethod
    def from_rc(cls: type[Self], r: int, c: int) -> Self:
        return cls(r, c)

    @classmethod
    def from_index(cls: type[Self], i: int) -> Self:
        return cls(cls._n_cols // i, cls._n_cols % i)

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        match = REGEX.fullmatch(v)
        row = _letters_to_number(match.group(1), cls._n_rows)
        col = int(match.group(2))
        return cls(row, col)

    @property
    def as_str(self: Self) -> str:
        return self.letter + str(self.col)

    @property
    def as_rc(self: Self) -> tuple[int, int]:
        return self.row, self.col

    @property
    def as_index(self: Self) -> int:
        return self._n_cols * (self.row - 1) + self.col

    @property
    def letter(self: Self) -> str:
        return _number_to_letters(self.row, self._n_rows)
