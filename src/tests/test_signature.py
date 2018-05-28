import os

import attr
import pytest
from eth_account import Account

from ..contracts.SpritesRegistry import SpritesRegistry
from ..channel import Payment, ChannelState, SignedState
from ..util import defunct_hash_message, hash_and_sign, check_tx, GAS
from ..exceptions import BadSignature, TransactionFailed


@pytest.fixture
def signed_payment(mock_channel, alice):
    p = Payment()


@pytest.fixture
def message():
    return b"hello"


@pytest.fixture
def msg_hash(message):
    return defunct_hash_message(message)


@pytest.fixture
def signature(message, alice):
    return hash_and_sign(message, alice.privateKey)


@pytest.fixture
def vrs(signature):
    return [signature.v, signature.r, signature.s]


def test_ecrecover_simple_message_success(alice, message, msg_hash, signature, vrs):
    for kwargs in [{"signature": signature.signature}, {"vrs": vrs}]:
        recovered = Account.recoverHash(msg_hash, **kwargs)
        assert recovered == alice.address


def test_ecrecover_contract_success(
    registry: SpritesRegistry, alice, message, msg_hash, vrs
):
    recovered = registry.recoverAddress(msg_hash, vrs).call()
    assert recovered == alice.address


def test_ecrecover_contract_wrong_hash_fails(
    web3, registry: SpritesRegistry, alice, vrs, deployer, tx_args
):
    bad_hash = os.urandom(32)
    recovered = registry.recoverAddress(bad_hash, vrs).call()
    assert recovered != alice.address

    tx_hash = registry.isSignatureOkay(alice.address, bad_hash, vrs).transact(tx_args)
    with pytest.raises(TransactionFailed):
        check_tx(web3, tx_hash)


@pytest.fixture
def signed_state(last_state, acting_party) -> SignedState:
    return last_state.sign(private_key=acting_party.privateKey)


def test_recover_address_from_channel_state(last_state, signed_state, acting_party):
    address = signed_state.recover_address()
    assert address == acting_party.address


@pytest.fixture
def modified_state(signed_state, new_state):
    return signed_state.to(**attr.asdict(new_state, recurse=False))


@pytest.mark.parametrize("new_round", [0, 1])
@pytest.mark.parametrize("new_amount", [0, 1, -1])
@pytest.mark.parametrize("new_credits", [[-2, 3], [-3, 2]])
@pytest.mark.parametrize("new_deposits", [[3, 1], [4, 0], [3, -1]])
def test_verify_signature_of_bad_channel_state_fails(acting_party, modified_state):
    """If another state was signed the channel state validation should fail"""
    with pytest.raises(BadSignature):
        modified_state.verify_signature(acting_party)
