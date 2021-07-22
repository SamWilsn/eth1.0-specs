"""
Utility Functions
^^^^^^^^^^^^^^^^^

..contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Utility functions used in this application.
"""
import dataclasses
from typing import Type, TypeVar, cast

from ethereum.base_types import Uint


def get_sign(value: int) -> int:
    """
    Determines the sign of a number.

    Parameters
    ----------
    value : `int`
        The value whose sign is to be determined.

    Returns
    -------
    sign : `int`
        The sign of the number (-1 or 0 or 1).
        The return value is based on math signum function.
    """
    if value < 0:
        return -1
    elif value == 0:
        return 0
    else:
        return 1


def ceil32(value: Uint) -> Uint:
    """
    Converts a unsigned integer to the next closest multiple of 32.

    Parameters
    ----------
    value :
        The value whose ceil32 is to be calculated.

    Returns
    -------
    ceil32 : `ethereum.base_types.U256`
        The same value if it's a perfect multiple of 32
        else it returns the smallest multiple of 32
        that is greater than `value`.
    """
    ceiling = Uint(32)
    remainder = value % ceiling
    if remainder == Uint(0):
        return value
    else:
        return value + ceiling - remainder


T = TypeVar("T")


def mutable(name: str, cls: Type[T]) -> Type[T]:
    """
    Generate a mutable version of a frozen dataclass.

    Parameters
    ----------
    name :
        The name of the class.
    cls :
        The `dataclass` to use as a template for the new class.
    Returns
    -------
    mutable : `Type`
        A new dataclass with the same fields as `cls`.
    """
    cls_mutable = type(
        name,
        (),
        {
            "__annotations__": cls.__dict__.get("__annotations__", {}),
            "__doc__": cls.__dict__.get("__doc__", None),
        },
    )

    # XXX: This cast tricks mypy into thinking the annotations on `cls` also
    #      apply to the newly generated class. The new class is *not* a real
    #      subclass of `cls`, but it does satisfy the same "protocol" (sorta).
    return cast(Type[T], dataclasses.dataclass(cls_mutable))
