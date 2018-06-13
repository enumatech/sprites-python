import pytest


@pytest.fixture
def channels(alice, bob, charlie, token, deposit_amount):

    channels = []

    for left, right in zip([alice, bob], [bob, charlie]):
        channel = left.open_channel(right, token)
        left.deposit(channel, deposit_amount)
        channels.append(channel)

    return channels


@pytest.mark.skip
def test_linked_payment(alice, bob, charlie, channels, amount):

    # desired
    path = alice.find_path(charlie, amount=amount)

    alice.create_topic(payment_id)




    linked_payment = alice.linked_payment([bob, charlie], amount)

    charlie.receive_payment_secret(linked_payment.secret)

    alice.open_payment(bob, amount)
    bob.open_payment(charlie, amount)

    charlie.publish([alice, bob], linked_payment.secret)

    alice.complete_payment()
    bob.complete_payment()
