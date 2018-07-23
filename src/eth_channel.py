import copy
import logging
from typing import Dict, List

import attr
from attr.validators import instance_of
from eth_account import Account
from eth_utils import keccak
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput

from .contracts.PreimageManager import PreimageManager
from .contracts.SpritesEthRegistry import SpritesEthRegistry
from .exceptions import (
    BadSignature, ForbiddenStateChange, Overpayment, Overwithdrawal, PaymentError
)
from .util import (
    COMMANDS,
    DELTA,
    ZERO_ADDRESS,
    ZERO_PREIMAGE_HASH,
    TransactionFailed,
    check_tx,
    hash_message,
    pack,
    sign,
)

log = logging.getLogger(__name__)

GAS = 4_000_000

# XXX If this is changed in contract need to update here.
# TODO get it from SpritesRegistry signature directly.
UPDATE_ARGUMENTS = [
    "channel_id",
    "sig",
    "credits",
    "withdrawals",
    "round",
    "preimage_hash",
    "recipient",
    "amount",
    "expiry",
]
MESSAGE_INPUTS = [arg for arg in UPDATE_ARGUMENTS if arg != "sig"]


@attr.s
class Base:

    def to(self, *args, **kwargs):
        return attr.evolve(copy.deepcopy(self), *args, **kwargs)


@attr.s(auto_attribs=True)
class Channel(Base):

    web3: Web3
    registry: SpritesEthRegistry
    preimage_manager: PreimageManager
    channel_id: int
    left: str
    right: str

    def deposit(self, sender, amount):


        tx_args = {"from": sender.address, "gas": GAS}
        # tx_hash = token.approve(self.registry._contract.address, amount).transact(
        #     tx_args
        # )

        # receipt = check_tx(self.web3, tx_hash)

        # can we inject the tx arguments instead?
        tx_hash = self.registry.deposit(self.channel_id, amount).transact(tx_args)
        receipt = check_tx(self.web3, tx_hash)

        return receipt

    def get_deposit(self, who=None, side=None):
        who = who or getattr(self, side)
        return self.registry.getDeposit(self.channel_id).call({"from": who.address})

    def get_status(self):
        return self.registry.getStatus(self.channel_id).call()

    def get_deadline(self):
        return self.registry.getDeadline(self.channel_id).call()

    def get_withdrawn(self, who):
        return self.registry.getWithdrawn(self.channel_id).call({"from": who.address})

    # TODO methods below follow similar patterns, refactor.

    def withdraw(self, who=None, side=None):
        who = who or getattr(self, side)
        tx_hash = self.registry.withdraw(self.channel_id).transact(
            {"from": who.address, "gas": GAS}
        )
        check_tx(self.web3, tx_hash)

    def trigger(self, who=None, side=None):
        who = who or getattr(self, side)
        tx_hash = self.registry.trigger(self.channel_id).transact(
            {"from": who.address, "gas": GAS}
        )
        check_tx(self.web3, tx_hash)

    def finalize(self, who=None, side=None):
        who = who or getattr(self, side)
        tx_hash = self.registry.finalize(self.channel_id).transact(
            {"from": who.address, "gas": GAS}
        )
        check_tx(self.web3, tx_hash)

    def get_state(self, who):
        state = self.registry.getState(self.channel_id).call({"from": who.address})
        payment = Payment(*state[-4:])
        channel_state = ChannelState(self.channel_id, *state[:-4], payment=payment)
        return channel_state

    def conditional_payment(self, sender, recipient, amount, preimage):
        # create new desired channel state
        channel_state = self.get_state(sender)
        expiry = self.web3.eth.blockNumber + DELTA
        new_state = channel_state.conditional_payment(
            amount=amount, recipient=recipient, expiry=expiry, preimage=preimage
        )
        signed_state = new_state.sign(private_key=sender.privateKey)
        return signed_state

    def update(self, who, args, check=False):
        log.debug("updating state %s %s", who, args)
        call = self.registry.update(*args)
        tx_args = {"from": who.address, "gas": GAS}

        if check:
            try:
                call.call(tx_args)
            except BadFunctionCallOutput as exc:
                raise TransactionFailed from exc

        tx_hash = call.transact(tx_args)
        check_tx(self.web3, tx_hash)

    def submit_preimage(self, who, preimage):
        log.debug("submitting preimage %s", preimage)
        tx_args = {"from": who.address, "gas": GAS}
        tx_hash = self.preimage_manager.submitPreimage(preimage).transact(tx_args)
        check_tx(self.web3, tx_hash)


@attr.s
class Payment(Base):
    preimage_hash = attr.ib(
        converter=bytes, validator=instance_of(bytes), default=ZERO_PREIMAGE_HASH
    )
    recipient = attr.ib(validator=instance_of(str), default=ZERO_ADDRESS)
    amount = attr.ib(validator=instance_of(int), default=0)
    expiry = attr.ib(validator=instance_of(int), default=0)
    command = attr.ib(default=None)

    def channel_state_update_arguments(self):
        return {
            k: v for k, v in attr.asdict(self).items() if k in set(UPDATE_ARGUMENTS)
        }


@attr.s
class ChannelState(Base):
    channel_id = attr.ib(validator=instance_of(int), default=0)
    deposits = attr.ib(validator=instance_of(list), default=[0, 0])
    credits = attr.ib(validator=instance_of(list), default=[0, 0])
    withdrawals = attr.ib(validator=instance_of(list), default=[0, 0])
    round = attr.ib(validator=instance_of(int), default=0)
    payment = attr.ib(validator=instance_of(Payment), default=Payment())

    def state_data(self):
        return {
            **self.channel_state_update_arguments(),
            **self.payment.channel_state_update_arguments(),
        }

    def to_other(self):
        return self.to(
            deposits=self.deposits[::-1],
            credits=self.credits[::-1],
            withdrawals=self.withdrawals[::-1],
        )

    def state_update_arguments(self):
        state_data = self.state_data()
        return tuple(state_data[k] for k in UPDATE_ARGUMENTS)

    def channel_state_update_arguments(self):
        return {
            k: v for k, v in attr.asdict(self).items() if k in set(UPDATE_ARGUMENTS)
        }

    def message_hash(self):
        state_data = self.state_data()
        message_parts = (state_data[k] for k in MESSAGE_INPUTS)
        return hash_message(pack(message_parts))

    def sign(self, private_key):
        log.debug("signing %s", self)
        signature = sign(self.message_hash(), private_key)
        sig = [signature.v, signature.r, signature.s]
        return SignedState(sig=sig, **attr.asdict(self, recurse=False))

    def make_payment(self, amount, recipient, expiry, preimage):
        preimage_hash = keccak(preimage)
        return Payment(preimage_hash, recipient, amount, expiry)

    def conditional_payment(self, recipient, amount, expiry, preimage):
        log.debug("adding payment %s to %s", amount, recipient)
        # XXX need to reserve credits for payment
        payment = self.make_payment(amount, recipient, expiry, preimage)
        new_credits = [self.credits[0] - amount, self.credits[1]]
        new_state = self.to(payment=payment, round=self.round + 1, credits=new_credits)
        return new_state

    def complete_payment(self):
        log.debug("completing payment %s", self.payment)
        # credit current payment to other party
        credits = [self.credits[0], self.credits[1] + self.payment.amount]
        # reset pending payment
        return attr.evolve(credits=credits, payment=Payment())

    def _check_credit(self, new_state):

        if new_state.credits[0] != self.credits[0]:
            raise ForbiddenStateChange("Their credits changed")

        if new_state.credits[1] != self.credits[1]:
            raise ForbiddenStateChange("Our credits changed")

    def _check_deposit(self, new_state):

        if new_state.deposits[0] != self.deposits[0]:
            # XXX need to check against contracti
            raise ForbiddenStateChange("Their deposit changed")

        if new_state.deposits[1] != self.deposits[1]:
            raise ForbiddenStateChange("Our deposit changed")

    def _check_withdrawal(self, new_state):

        if new_state.withdrawals[1] != self.withdrawals[1]:
            raise ForbiddenStateChange("Our withdrawal changed")

        new_withdrawal = new_state.withdrawals[0]
        new_deposit = new_state.deposits[0]
        new_credit = new_state.credits[0]

        if new_withdrawal > new_deposit + new_credit:
            raise Overwithdrawal(
                f"withdrawal={new_withdrawal} > deposit={new_deposit}"
                f"+ credit={new_credit}"
            )

    def _check_round_number(self, new_state):
        if new_state.round <= self.round:
            raise PaymentError(f"Round not advanced")

    def _validate_open(self, new_state):

        new_amount = new_state.payment.amount
        old_amount = self.payment.amount

        if old_amount != 0:
            raise PaymentError(f"Payment already in process")

        elif new_amount <= 0:
            raise PaymentError(f"Amount needs to positive, got {new_amount}")

        elif new_amount > self.deposits[0] + self.credits[0]:
            raise Overpayment(
                f"amount={new_amount} > deposit={self.deposits[0]} + "
                f"credit={self.credits[0]}"
            )

        elif new_state.credits[0] != self.credits[0] - new_state.payment.amount:
            raise PaymentError("Credits for payment not correctly reserved")

    def _validate_complete(self, new_state):

        new_amount = new_state.payment.amount
        old_amount = self.payment.amount

        if old_amount == 0:
            raise PaymentError(f"No payment to complete")

        elif new_amount != 0:
            raise PaymentError(f"Amount needs to be 0 to complete, got {new_amount}")

        elif self.credits[1] + old_amount != new_state.credits[1]:
            raise PaymentError(f"Payment not credited to recipient.")

        elif self.credits[0] != new_state.credits[0]:
            raise PaymentError(f"Opponent changed his credits.")

        self._check_unchanged(new_state, ["deposits", "withdrawals"])

    def _validate_cancel(self, new_state):

        new_amount = new_state.payment.amount
        old_amount = self.payment.amount

        if old_amount == 0:
            raise PaymentError(f"No payment to cancel")

        elif new_amount != 0:
            raise PaymentError(f"Amount should be 0 after cancel, got {new_amount}")

        if self.credits[0] + old_amount != new_state.credits[0]:
            raise PaymentError(f"Payment amount wrongly credited")

    def _check_unchanged(self, new_state, attributes):
        for attribute in attributes:
            if getattr(self, attribute) != getattr(new_state, attribute):
                raise PaymentError(f"{attribute} changed")

    def _validate_update(self, new_state):
        self._check_credit(new_state)
        self._check_deposit(new_state)
        self._check_withdrawal(new_state)

    def validate(self, new_state, command=None):

        self._check_round_number(new_state)

        if command is not None and command not in COMMANDS:
            raise ValueError(f"command {command} not in {COMMANDS} (or None)")

        if command == "open":
            self._validate_open(new_state)
        elif command == "complete":
            self._validate_complete(new_state)
        elif command == "cancel":
            self._validate_cancel(new_state)
        else:
            # non-commands simply update the state?
            self._validate_update(new_state)


@attr.s
class SignedState(ChannelState):
    # XXX don't want default here, but can't have mandatory attributes
    # after optional ones.
    sig = attr.ib(validator=instance_of(list), default=None)

    def to_unsigned(self) -> ChannelState:
        return ChannelState(
            **attr.asdict(
                self, recurse=False, filter=lambda attribute, _: attribute.name != "sig"
            )
        )

    def recover_address(self):
        msg_hash = self.message_hash()
        return Account.recoverHash(msg_hash, vrs=self.sig)

    def verify_signature(self, address):
        if self.recover_address() != address:
            raise BadSignature("Recovered address incorrect")


@attr.s(auto_attribs=True)
class Player:
    channels: Dict[str, Channel]
    payments: Dict[str, List[Payment]]

    def receive_payment(self, payment: Payment) -> None:
        # validate payment signature + deposits of other party
        raise NotImplementedError

    def make_payment(self, channel_id, amount) -> Payment:
        raise NotImplementedError
