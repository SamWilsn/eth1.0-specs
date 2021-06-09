"""
EVM Stack Operators
----------------------
"""

from typing import List

from ..eth_types import U256
from .error import StackOverflowError, StackUnderflowError


def pop(stack: List[U256]) -> U256:
    """
    Pops the top item off of `stack`.

    Parameters
    ----------
    stack : `List[U256]`
        EVM stack.

    Returns
    -------
    value : `U256`
        The top element on the stack.

    Raises
    ------
    StackUnderflowError
        If `stack` is empty.
    """
    if len(stack) == 0:
        raise StackUnderflowError

    return stack.pop()


def push(stack: List[U256], value: U256) -> None:
    """
    Pushes `value` onto `stack`.

    Parameters
    ----------
    stack : `List[U256]`
        EVM stack.

    value : `U256`
        Item to be pushed onto `stack`.

    Raises
    ------
    StackOverflowError
        If `len(stack)` is `1024`.
    """
    if len(stack) == 1024:
        raise StackOverflowError

    return stack.append(value)
