# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Realized
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/realized
# SPDX-License-Identifier: Apache-2.0

"""
Metadata and environment variables.
"""
import inspect
from typing import Iterable, Mapping, Self, TypeVar

__all__ = ["Utils"]
T_co = TypeVar("T_co", covariant=True)


class Utils:

    @classmethod
    def subclass_dict(
        cls: type[Self],
        clazz: type[T_co],
        concrete: bool = False,
    ) -> Mapping[str, type[T_co]]:
        return {c.__name__: c for c in cls._get_subclasses(clazz, concrete=concrete)}

    @classmethod
    def _get_subclasses(
        cls: type[Self],
        clazz: type[T_co],
        concrete: bool = False,
    ) -> Iterable[type[T_co]]:
        for subclass in clazz.__subclasses__():
            yield from cls._get_subclasses(subclass, concrete=concrete)
            if not concrete or not inspect.isabstract(subclass) and not subclass.__name__.startswith("_"):
                yield subclass
