import pytest

from ..util import wait_blocks, DELTA


@pytest.fixture
def channel_weth(channel_with_deposit):
    return channel_with_deposit


@pytest.fixture
def channel_oax(other_channel_with_deposit):
    return other_channel_with_deposit


def test_token_swap_dispute(
    web3,
    acting_party,
    other_party,
    channel_weth,
    channel_oax,
    preimage,
    token,
    other_token,
):
    """This is just an example of how a 2 party token swap could go down."""

    channel_weth_state = channel_weth.get_state(who=acting_party)
    channel_oax_state = channel_oax.get_state(who=other_party)

    amount_weth = 4
    amount_oax = 7
    payment_weth = channel_weth.conditional_payment(
        sender=acting_party,
        recipient=other_party.address,
        amount=amount_weth,
        preimage=preimage,
    )
    # The receiving party validates the conditional payment
    channel_weth_state.validate(payment_weth, command="open")

    payment_oax = channel_oax.conditional_payment(
        sender=other_party,
        recipient=acting_party.address,
        amount=amount_oax,
        preimage=preimage,
    )
    channel_oax_state.validate(payment_oax, command="open")

    # Now save to send preimage to other party.
    # Assume that happens but no further cooperation occurs (no unconditional payments).
    # Both parties submit preimage to make sure their incoming payment succeeds.

    # ---------- Settle via forced on-chain transfer in both channels ----------

    channel_weth.trigger(who=other_party)
    channel_weth.submit_preimage(other_party, preimage)
    channel_weth.update(who=other_party, args=payment_weth.state_update_arguments())

    # Assume acting party gets an event via trigger and triggers dispute in the
    # channel where they are receiving.
    channel_oax.trigger(who=acting_party)
    # Preimage is already submitted.
    channel_oax.update(who=acting_party, args=payment_oax.state_update_arguments())

    wait_blocks(web3, DELTA)

    channel_weth.finalize(who=acting_party)
    channel_oax.finalize(who=other_party)

    state_weth = channel_weth.get_state(who=acting_party)
    assert state_weth.withdrawals == [
        channel_weth_state.deposits[0] - amount_weth,
        channel_weth_state.deposits[1] + amount_weth,
    ]

    state_oax = channel_oax.get_state(who=other_party)
    assert state_oax.withdrawals == [
        channel_oax_state.deposits[0] - amount_oax,
        channel_oax_state.deposits[1] + amount_oax,
    ]
