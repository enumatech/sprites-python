import functools
import json
import logging
import os

from eth_account import Account
from eth_account.messages import defunct_hash_message
from tenacity import after_log, retry, retry_if_exception_type
from web3.utils import encoding

from .exceptions import TransactionFailed

log = logging.getLogger(__name__)

GAS = 4_000_000
LOTS = 10 ** 18
DELTA = 2  # needs to match contract DELTA
ZERO_PREIMAGE_HASH = bytes(32)
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
COMMANDS = ["open", "complete", "cancel"]


def to_bytes(primitive):

    if isinstance(primitive, str):
        return encoding.to_bytes(hexstr=primitive)

    if isinstance(primitive, int):
        if primitive < -(1 << 255) or primitive > (1 << 255):
            raise ValueError(f"int {primitive} out of range")

        value = ((1 << 256) + primitive) if primitive < 0 else primitive
    else:
        value = primitive

    encoded = encoding.to_bytes(primitive=value)
    return encoded


def pad(s):
    return s.rjust(32, b"\0")


def flatten(args):
    for arg in args:
        if isinstance(arg, (tuple, list)):
            for item in arg:
                yield item

        else:
            yield arg


def pack(args):
    return b"".join(pad(to_bytes(arg)) for arg in flatten(args))


def generate_preimage():
    return os.urandom(32)


def hash_and_sign(msg_bytes, private_key):
    return sign(hash_message(msg_bytes), private_key)


def hash_message(msg_bytes):
    return defunct_hash_message(msg_bytes)


def sign(hash_to_sign, private_key):
    return Account.signHash(hash_to_sign, private_key)


def check_status(fun):

    @functools.wraps(fun)
    def wrapper(web3, *args, **kwargs):
        tx_hash = fun(web3, *args, **kwargs)
        return check_tx(web3, tx_hash)

    return wrapper


@retry(
    retry=retry_if_exception_type(AttributeError), after=after_log(log, logging.DEBUG)
)
def check_tx(web3, tx_hash):
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    if receipt.status != 1:
        raise TransactionFailed(f"TX status 0: {receipt}")

    return receipt


def tx_args(web3, sender=None, gas=GAS, **kwargs):
    sender = sender or _default_account(web3)
    return {"from": sender, "gas": GAS, **kwargs}


def _default_account(web3):
    return web3.eth.accounts[0]


@check_status
def fund_eth(web3, to, amount=LOTS):
    return web3.eth.sendTransaction(tx_args(web3, to=to, value=LOTS))


@check_status
def fund_token(web3, token, sender, to, amount):
    return token.transfer(to, amount).transact(tx_args(web3))


@check_status
def mint(web3, token, recipient):
    return token.mint(recipient, LOTS).transact(tx_args(web3))


def fund_account(web3, guy, account):
    tx_hash = web3.eth.sendTransaction(
        {"to": account.address, "value": LOTS, "from": guy, "gas": GAS}
    )
    check_tx(web3, tx_hash)


def load_contract(fname, name):
    with open("out/contracts.json") as filehandle:
        contracts = json.load(filehandle)
    path = os.path.join("contracts", f"{fname}:{name}")
    return contracts["contracts"][path]


def deploy_contract(web3, deployer, fname, name, cls, args=()):

    log.debug("deploying contract %s %s with args %s", fname, name, args)

    contract = load_contract(fname, name)
    Contract = web3.eth.contract(abi=contract["abi"], bytecode=contract["bin"])

    deploy_hash = Contract.constructor(*args).transact({"from": deployer, "gas": GAS})
    receipt = check_tx(web3, deploy_hash)

    contract_address = receipt["contractAddress"]

    log.debug("deployed contract %s %s at %s", fname, name, contract_address)

    web3_contract = Contract(address=contract_address)

    return cls(web3_contract)


def noop_tx(web3):
    return web3.eth.sendTransaction(tx_args(web3, to=_default_account(web3)))


def wait_blocks(web3, num_blocks):
    for _ in range(num_blocks):
        noop_tx(web3)
