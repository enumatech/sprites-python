import pytest

from ..exceptions import ForbiddenStateChange, Overpayment, Overwithdrawal, PaymentError

p = pytest.mark.parametrize


@p("new_amount", [5])
def test_overpayment_fails(amount, last_state, new_state):
    with pytest.raises(Overpayment):
        last_state.validate(new_state, command="open")


@p("deposits", [[5, 0]])
@p("new_credits", [[-3, 0]])
@p("new_amount", [3])
def test_valid_open_payment_passes(last_state, new_state):
    last_state.validate(new_state, command="open")


@p("deposits", [[3, 0]])
@p("new_withdrawals", [[3, 0]])
def test_valid_withdrawal_passes(last_state, new_state):
    last_state.validate(new_state)


@p("deposits", [[3, 0]])
@p("new_withdrawals", [[4, 0]])
def test_overwithdraw_fails(last_state, new_state):
    with pytest.raises(Overwithdrawal):
        last_state.validate(new_state)


@p("new_credits", [[0, -1]])
def test_changing_other_credits_fails(last_state, new_state):
    with pytest.raises(ForbiddenStateChange):
        last_state.validate(new_state)


@p("new_withdrawals", [[0, 1]])
def test_changing_other_withdrawals_fails(last_state, new_state):
    with pytest.raises(ForbiddenStateChange):
        last_state.validate(new_state)


@p("credits", [[0, 0]])
@p("new_credits", [[1, 0]])
def test_inflating_credits_fails(last_state, new_state):
    with pytest.raises(ForbiddenStateChange):
        last_state.validate(new_state)


@p("credits", [[0, 0]])
@p("new_credits", [[0, -1]])
def test_changing_other_withdrawal_fails(last_state, new_state):
    with pytest.raises(ForbiddenStateChange):
        last_state.validate(new_state)


@p("deposits", [[3, 0]])
@p("credits", [[-3, 0]])
@p("amount", [3])
@p("new_amount", [0])
@p("new_credits", [[-3, 3]])
def test_complete_payment_valid(last_state, new_state):
    last_state.validate(new_state, command="complete")


@p("round", [0])
@p("new_round", [0, 1])
@p("deposits", [[3, 0]])
@p("credits", [[-3, 0]])
@p("amount", [3, 0])
@p("new_amount", [0, 1, -1])
@p("new_credits", [[-2, 3], [-3, 2]])
@p("new_deposits", [[3, 1], [4, 0], [3, -1]])
def test_complete_payment(last_state, new_state):
    checks = [
        new_state.round > last_state.round,
        last_state.payment.amount != 0,
        new_state.payment.amount == 0,
        last_state.deposits == new_state.deposits,
        last_state.withdrawals == new_state.withdrawals,
    ]
    if not all(checks):
        with pytest.raises(PaymentError):
            last_state.validate(new_state, command="complete")


@p("deposits", [[3, 0]])
@p("credits", [[-3, 0]])
@p("amount", [3])
@p("new_amount", [0])
@p("new_credits", [[0, 0]])
def test_cancel_payment_valid(last_state, new_state):
    last_state.validate(new_state, command="cancel")


@p("round", [0])
@p("new_round", [0, 1])
@p("deposits", [[3, 0]])
@p("credits", [[-3, 0]])
@p("amount", [3, 0])
@p("new_amount", [0, 1, -1])
@p("new_credits", [[-2, 3], [-3, 2]])
@p("new_deposits", [[3, 1], [4, 0], [3, -1]])
def test_cancel_payment(last_state, new_state):
    checks = [
        new_state.round > last_state.round,
        last_state.payment.amount != 0,
        new_state.payment.amount == 0,
        last_state.deposits == new_state.deposits,
        last_state.withdrawals == new_state.withdrawals,
    ]
    if not all(checks):
        with pytest.raises(PaymentError):
            last_state.validate(new_state, command="cancel")
