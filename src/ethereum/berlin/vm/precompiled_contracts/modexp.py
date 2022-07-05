"""
Ethereum Virtual Machine (EVM) MODEXP PRECOMPILED CONTRACT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: Table of Contents
    :backlinks: none
    :local:

Introduction
------------

Implementation of the `MODEXP` precompiled contract.
"""
from ethereum.base_types import U256, Bytes, Uint
from ethereum.utils.byte import right_pad_zero_bytes

from ...vm import Evm
from ...vm.gas import subtract_gas
from ..exceptions import OutOfGasError

GQUADDIVISOR = 20


def modexp(evm: Evm) -> None:
    """
    Calculates `(base**exp) % modulus` for arbitary sized `base`, `exp` and.
    `modulus`. The return value is the same length as the modulus.
    """
    data = evm.message.data
    base_length = U256.from_be_bytes(right_pad_zero_bytes(data[:32], 32))
    exp_length = U256.from_be_bytes(right_pad_zero_bytes(data[32:64], 32))
    modulus_length = U256.from_be_bytes(right_pad_zero_bytes(data[64:96], 32))

    if base_length == 0 and modulus_length == 0:
        evm.output = Bytes()
        return

    if evm.gas_left < gas_cost(base_length, modulus_length, exp_length, 0):
        # This check must be done now to prevent loading of absurdly long
        # arguments. It is an underestimate, because adjusted_exp_length may
        # increase later.
        raise OutOfGasError()

    pointer = 96
    base_data = right_pad_zero_bytes(
        data[pointer : pointer + base_length], base_length
    )
    base = Uint.from_be_bytes(base_data)
    pointer += base_length
    exp_data = right_pad_zero_bytes(
        data[pointer : pointer + exp_length], exp_length
    )
    exp = Uint.from_be_bytes(exp_data)
    pointer += exp_length
    modulus_data = right_pad_zero_bytes(
        data[pointer : pointer + modulus_length], modulus_length
    )
    modulus = Uint.from_be_bytes(modulus_data)

    gas_used = gas_cost(base_length, modulus_length, exp_length, exp)

    # NOTE: It is in principle possible for the conversion to U256 to overflow
    # here. However, for this to happen without triggering the earlier check
    # would require providing more than 2**250 gas, which is obviously
    # not realistic.
    evm.gas_left = subtract_gas(evm.gas_left, U256(gas_used))
    if modulus == 0:
        evm.output = Bytes(b"\x00") * modulus_length
    else:
        evm.output = Uint(pow(base, exp, modulus)).to_bytes(
            modulus_length, "big"
        )


def complexity(base_length, modulus_length):
    max_length = max(base_length, modulus_length)
    words = (max_length + 7) // 8
    return words**2


def iterations(exponent_length, exponent):
    if exponent_length <= 32 and exponent == 0:
        count = 0
    elif exponent_length <= 32:
        count = exponent.bit_length() - 1
    else:
        length_part = 8 * (exponent_length - 32)
        bits_part = (exponent & (2**256 - 1)).bit_length() - 1
        count = length_part + bits_part

    return max(count, 1)


def gas_cost(base_length, modulus_length, exponent_length, exponent):
    multiplication_complexity = complexity(base_length, modulus_length)
    iteration_count = iterations(exponent_length, exponent)
    cost = multiplication_complexity * (iteration_count // GQUADDIVISOR)
    return max(200, cost)
