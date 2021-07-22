"""
Ethereum Types
^^^^^^^^^^^^^^

.. contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Types re-used throughout the specification, which are specific to Ethereum.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from ..base_types import U256, Bytes, Bytes8, Bytes20, Bytes32, Uint
from ..crypto import Hash32
from ..utils import mutable

Address = Bytes20
Root = Bytes

Storage = Dict[Bytes32, U256]
Bloom = Bytes32

TX_BASE_COST = 21000
TX_DATA_COST_PER_NON_ZERO = 68
TX_DATA_COST_PER_ZERO = 4


@dataclass
class Transaction:
    """
    Atomic operation performed on the block chain.
    """

    nonce: U256
    gas_price: U256
    gas: U256
    to: Optional[Address]
    value: U256
    data: Bytes
    v: U256
    r: U256
    s: U256


@dataclass
class Account:
    """
    State associated with an address.
    """

    nonce: Uint
    balance: Uint
    code: bytes
    storage: Storage


EMPTY_ACCOUNT = Account(
    nonce=Uint(0),
    balance=Uint(0),
    code=bytearray(),
    storage={},
)


AccountMutable = mutable("AccountMutable", Account)


@dataclass
class Header:
    """
    Header portion of a block on the chain.
    """

    parent_hash: Hash32
    ommers_hash: Hash32
    coinbase: Address
    state_root: Root
    transactions_root: Root
    receipt_root: Root
    bloom: Bloom
    difficulty: Uint
    number: Uint
    gas_limit: Uint
    gas_used: Uint
    timestamp: U256
    extra_data: Bytes
    mix_digest: Bytes32
    nonce: Bytes8


@dataclass
class Block:
    """
    A complete block.
    """

    header: Header
    transactions: List[Transaction]
    ommers: List[Header]


@dataclass
class Log:
    """
    Data record produced during the execution of a transaction.
    """

    address: Address
    topics: List[Hash32]
    data: bytes


@dataclass
class Receipt:
    """
    Result of a transaction.
    """

    post_state: Root
    cumulative_gas_used: Uint
    bloom: Bloom
    logs: List[Log]


State = Dict[Address, Account]


def state_modify(
    state: State,
    address: Address,
    transform: Callable[[Account], None],
) -> Account:
    """
    Modifies the account in the state according to `transform`.

    Parameters
    ----------
    state :
        The state storage object.
    address :
        Address of the account to modify.
    transform :
        A callable that applies changes to the given account object.

    Returns
    -------
    account : Account
        The account object after the modifications have been applied.
    """
    old_account = state.get(address, EMPTY_ACCOUNT)
    account_mutable = AccountMutable(**old_account.__dict__)
    transform(account_mutable)
    new_account = Account(**account_mutable.__dict__)

    if new_account != old_account:
        if new_account == EMPTY_ACCOUNT:
            del state[address]
        else:
            state[address] = new_account

    return new_account
