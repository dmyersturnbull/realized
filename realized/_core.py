# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from dataclasses import dataclass
from typing import Self, TypeAlias

import orjson


__all__ = ["JsonEncoder", "JsonPrimitive", "JsonType", "Model", "NullableInt", "NULL_INT"]

ORJSON_OPTS = (
    orjson.OPT_UTC_Z
    | orjson.OPT_SERIALIZE_NUMPY
    | orjson.OPT_STRICT_INTEGER  # 53-bit ints for JavaScript compat
    | orjson.OPT_NON_STR_KEYS
)
JsonPrimitive = None | bool | int | float | str

# Recursive JSON type definition
JsonType: TypeAlias = JsonPrimitive | list["JsonType"] | dict[str, "JsonType"]


class JsonEncoder:

    def to_json(self: Self, data: JsonType, options: int = 0) -> str:
        return orjson.dumps(data, option=options | ORJSON_OPTS).decode("utf-8")


@dataclass(slots=True, frozen=True, order=True)
class Model:

    @classmethod
    def from_str(cls: type[Self], v: str) -> Self:
        raise NotImplementedError()

    @classmethod
    def from_json(cls: type[Self], v: str) -> Self:
        return cls(**orjson.loads(v).encode("utf-8"))

    def __post_init__(self: Self) -> None:
        pass

    def __repr__(self: Self) -> str:
        return self.as_str

    def __str__(self: Self) -> str:
        return self.as_str

    def __reduce__(self: Self) -> tuple[Callable[[str], Self], tuple]:
        return self.__class__.from_str, (self.as_str,)

    @property
    def as_str(self: Self) -> str:
        raise NotImplementedError()

    def to_json(self: Self, *, options: int = 0) -> str:
        return JsonEncoder().to_json(self._json_data, options)

    @property
    def _json_data(self: Self) -> JsonType:
        return self.as_str  # default


class NullableInt(int):
    """
    A replacement for `int | None` for which only `None` is `False`; `0` is `True`.
    """

    @classmethod
    def null(cls: type[Self]) -> Self:
        return NullableInt(None)

    @classmethod
    def of(cls: type[Self], v: int) -> Self:
        if v is None:
            raise ValueError("Value is null")
        return NullableInt(v)

    def __new__(cls, num: int | None):
        return super(NullableInt, cls).__new__(cls, num)

    def __init__(self: Self, num: int | None) -> None:
        self.num = num

    def __bool__(self: Self):
        return self.num is not None


NULL_INT = NullableInt.null()
