from ethereum.base_types import Uint
from ethereum.frontier.eth_types import Account, State, state_modify


def test_state_modify_insert_new() -> None:
    state: State = {}

    def initial_balance(account: Account) -> None:
        account.balance = Uint(500)

    address = b"\x00" * 20

    state_modify(state, address, initial_balance)

    assert state == {
        address: Account(
            nonce=Uint(0),
            balance=Uint(500),
            code=bytearray(),
            storage={},
        )
    }


def test_state_modify_insert_empty() -> None:
    state: State = {}

    def do_nothing(account: Account) -> None:
        pass

    address = b"\x00" * 20

    state_modify(state, address, do_nothing)

    assert state == {}


def test_state_modify_remove() -> None:
    address = b"\x00" * 20
    state: State = {
        address: Account(
            nonce=Uint(3),
            balance=Uint(500),
            code=bytearray(),
            storage={},
        )
    }

    def erase(account: Account) -> None:
        account.nonce = Uint(0)
        account.balance = Uint(0)

    state_modify(state, address, erase)

    assert state == {}


def test_state_modify_update() -> None:
    address = b"\x00" * 20
    state: State = {
        address: Account(
            nonce=Uint(3),
            balance=Uint(500),
            code=bytearray(),
            storage={},
        )
    }

    def increment_nonce(account: Account) -> None:
        account.nonce += 1

    state_modify(state, address, increment_nonce)

    assert state == {
        address: Account(
            nonce=Uint(4),
            balance=Uint(500),
            code=bytearray(),
            storage={},
        )
    }
