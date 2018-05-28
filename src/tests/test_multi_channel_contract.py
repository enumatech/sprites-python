"""Test for Sprites Payment Channels"""
import pytest
from web3.utils.encoding import to_hex

from ..channel import Channel, Payment
from ..contracts.dappsys import DSToken
from ..contracts.SpritesRegistry import SpritesRegistry
from ..util import (
    DELTA,
    GAS,
    ZERO_ADDRESS,
    ZERO_PREIMAGE_HASH,
    TransactionFailed,
    fund_token,
    wait_blocks,
)

pytestmark = pytest.mark.usefixtures(
    "web3", "alice", "bob", "charlie", "acting_party", "other_party", "channel"
)

TOKEN_NAMES = ["WETH", "OAX"]
THIRD_PARTY_NAME = "charlie"
FUND_TOKEN_AMOUNT = 100
DEPOSIT_AMOUNTS = {"alice": 9, "bob": 10}
SEND_AMOUNT = 7
# two parties are equivalent / symmetric in many tests


@pytest.fixture
def deposit_amount(acting_party_name):
    return DEPOSIT_AMOUNTS[acting_party_name]


@pytest.fixture
def send_amount():
    return SEND_AMOUNT


def test_send_tokens(web3, token, acting_party, guy):
    fund_token(
        web3, token=token, sender=guy, to=acting_party.address, amount=FUND_TOKEN_AMOUNT
    )
    assert token.balanceOf(acting_party.address).call() == FUND_TOKEN_AMOUNT


@pytest.fixture
def with_tokens(web3, token, acting_party, guy):
    fund_token(
        web3, token=token, sender=guy, to=acting_party.address, amount=FUND_TOKEN_AMOUNT
    )
    return acting_party


@pytest.fixture
def channel_with_deposit(channel, acting_party, deposit_amount, with_tokens):
    channel.deposit(sender=acting_party, amount=deposit_amount)
    return channel


def test_channel_can_create_channel(
    web3, registry, token, acting_party, other_party, channel
):
    assert channel.left == acting_party
    assert channel.right == other_party
    assert channel.token == token
    for side in ["left", "right"]:
        assert channel.get_deposit(side=side) == 0


def test_channel_initial_state(channel, acting_party):
    state = channel.get_state(who=acting_party)
    assert state.deposits == [0, 0]
    assert state.credits == [0, 0]
    assert state.withdrawals == [0, 0]
    assert state.round == -1

    payment = state.payment
    assert payment.preimage_hash == ZERO_PREIMAGE_HASH
    assert payment.expiry == 0
    assert payment.amount == 0
    assert payment.recipient == ZERO_ADDRESS


def test_deposit_can_deposit(channel, acting_party, with_tokens, deposit_amount):
    channel.deposit(acting_party, amount=deposit_amount)
    assert channel.get_deposit(who=acting_party) == deposit_amount


def test_deposit_cannot_deposit_other_token(
    channel, acting_party, deposit_amount, other_token
):
    with pytest.raises(TransactionFailed):
        channel.deposit(acting_party, amount=deposit_amount, token=other_token)
    assert channel.get_deposit(who=acting_party) == 0


def test_deposit_unauthorized_party_cannot_deposit(
    channel, third_party, deposit_amount
):
    with pytest.raises(TransactionFailed):
        channel.deposit(sender=third_party, amount=deposit_amount)
    assert channel.get_deposit(side="left") == 0
    assert channel.get_deposit(side="right") == 0


@pytest.mark.usefixtures("channel_with_deposit")
def test_deposit_can_make_additional_deposit(channel, acting_party, deposit_amount):
    original_deposit = channel.get_deposit(who=acting_party)
    assert original_deposit > 0
    channel.deposit(acting_party, amount=deposit_amount)
    assert channel.get_deposit(who=acting_party) == original_deposit + deposit_amount


@pytest.mark.usefixtures("channel_with_deposit")
def test_withdraw_cannot_withdraw_without_trigger(token, channel, acting_party):
    original_balance = token.balanceOf(acting_party.address).call()
    channel.withdraw(who=acting_party)
    assert token.balanceOf(acting_party.address).call() == original_balance


# XXX the fixture on top is executed last?


@pytest.mark.usefixtures("finalized_channel")
def test_withdraw_can_withdraw(web3, token, channel, acting_party):
    channel.withdraw(who=acting_party)
    assert token.balanceOf(acting_party.address).call() == FUND_TOKEN_AMOUNT


@pytest.fixture
def triggered_mock_channel(mock_channel, acting_party):
    mock_channel.trigger(who=acting_party)
    return mock_channel


@pytest.fixture
def finalized_channel(web3, channel_with_deposit, acting_party):
    channel_with_deposit.trigger(who=acting_party)

    # wait DELTA blocks ...
    wait_blocks(web3, num_blocks=DELTA)
    channel_with_deposit.finalize(who=acting_party)

    return channel_with_deposit


@pytest.mark.usefixtures("finalized_channel")
def test_withdraw_unauthorized_party_cannot_withdraw(
    token, channel, acting_party, third_party
):
    with pytest.raises(TransactionFailed):
        channel.withdraw(who=third_party)
    assert token.balanceOf(third_party.address).call() == 0
    assert channel.get_withdrawn(acting_party) == 0


@pytest.mark.skip
def test_withdraw_cannot_withdraw_from_opponent(acting_party, other_party):
    raise NotImplementedError


@pytest.fixture
def signed_state_inflight_payment(
    channel_with_deposit, acting_party, other_party, preimage, send_amount
):
    return channel_with_deposit.conditional_payment(
        sender=acting_party,
        recipient=other_party.address,
        amount=send_amount,
        preimage=preimage,
    )


def test_channel_update_succeeds(
    channel, acting_party, other_party, signed_state_inflight_payment
):

    args = signed_state_inflight_payment.state_update_arguments()

    channel.update(who=other_party, args=args)
    returned_state = channel.get_state(who=acting_party)

    assert signed_state_inflight_payment.to_unsigned() == returned_state


@pytest.mark.skip
def test_update_channel_state_with_credits():
    """Need check if left/right side is handled correctly"""
    raise NotImplementedError


@pytest.mark.skip
def test_update_channel_state_with_withdrawals():
    """Need check if left/right side is handled correctly"""
    raise NotImplementedError


def test_payment_contract_refuses_overpayment(
    channel_with_deposit, acting_party, other_party, deposit_amount, preimage
):
    signed_state_with_overpayment = channel_with_deposit.conditional_payment(
        sender=acting_party,
        recipient=other_party.address,
        amount=deposit_amount + 1,
        preimage=preimage,
    )
    args = signed_state_with_overpayment.state_update_arguments()

    original_state = channel_with_deposit.get_state(who=acting_party)
    # check that update and check update fail
    for check in [True, False]:
        with pytest.raises(TransactionFailed):
            channel_with_deposit.update(who=other_party, args=args, check=True)
            new_state = channel_with_deposit.get_state(who=acting_party)
            assert original_state == new_state


@pytest.mark.skip
def test_transfer_full_payment_through_channel(acting_party):
    raise NotImplementedError


def test_trigger_trigger_sets_pending(mock_channel, acting_party):
    assert mock_channel.get_status() == 0
    mock_channel.trigger(who=acting_party)
    assert mock_channel.get_status() == 1


def test_trigger_trigger_sets_deadline(web3, mock_channel, acting_party):
    mock_channel.trigger(who=acting_party)
    block_number = web3.eth.blockNumber
    assert mock_channel.get_deadline() == block_number + DELTA


def test_trigger_trigger_twice_fails(channel, acting_party):
    channel.trigger(who=acting_party)
    with pytest.raises(TransactionFailed):
        channel.trigger(who=acting_party)


def test_trigger_unauthorized_party_cannot_trigger(mock_channel, third_party):
    assert mock_channel.get_status() == 0
    with pytest.raises(TransactionFailed):
        mock_channel.trigger(who=third_party)
    assert mock_channel.get_status() == 0


def test_finalize_finalize_requires_pending_status(mock_channel, acting_party):
    with pytest.raises(TransactionFailed):
        mock_channel.finalize(who=acting_party)


def test_finalize_finalize_fails_before_deadline(triggered_mock_channel, acting_party):
    with pytest.raises(TransactionFailed):
        triggered_mock_channel.finalize(who=acting_party)


@pytest.mark.usefixtures("triggered_mock_channel")
def test_finalize_finalize_succeeds_after_deadline(web3, mock_channel, acting_party):
    wait_blocks(web3, DELTA)
    mock_channel.finalize(who=acting_party)
    state = mock_channel.get_state(who=acting_party)

    # channel had no deposits or payments, should all be empty still
    assert state.withdrawals == [0, 0]
    assert state.credits == [0, 0]
    assert state.payment == Payment()


def test_finalize_dispute_payment_completes_on_chain(
    web3,
    acting_party,
    other_party,
    channel,
    signed_state_inflight_payment,
    deposit_amount,
    send_amount,
    preimage,
):
    args = signed_state_inflight_payment.state_update_arguments()

    channel.update(who=other_party, args=args)
    channel.submit_preimage(who=other_party, preimage=preimage)
    channel.trigger(who=other_party)

    wait_blocks(web3, DELTA)

    channel.finalize(who=other_party)

    state = channel.get_state(who=acting_party)

    assert state.deposits == [deposit_amount, 0]
    assert state.credits == [-deposit_amount, 0]
    assert state.withdrawals == [deposit_amount - send_amount, send_amount]


# TODO decribe all scenarios (submit/not submit, wait/no wait ... )


def test_finalize_dispute_payment_cancels_off_chain(
    web3,
    acting_party,
    other_party,
    channel,
    signed_state_inflight_payment,
    deposit_amount,
    send_amount,
    preimage,
):
    args = signed_state_inflight_payment.state_update_arguments()

    channel.update(who=other_party, args=args)

    # no submission

    channel.trigger(who=other_party)

    wait_blocks(web3, DELTA)

    channel.finalize(who=other_party)

    state = channel.get_state(who=acting_party)

    assert state.deposits == [deposit_amount, 0]
    assert state.credits == [-deposit_amount, 0]
    assert state.withdrawals == [deposit_amount, 0]


def test_finalize_unauthorized_party_cannot_finalize(mock_channel, other_party):
    with pytest.raises(TransactionFailed):
        mock_channel.finalize(who=other_party)
