from collections import namedtuple
from time import sleep

import eth_account
import pytest
from eth_utils.address import to_checksum_address
from web3 import HTTPProvider, Web3
from web3.middleware import geth_poa_middleware

from ..channel import Channel, ChannelState, Payment
from ..eth_channel import Channel as EthChannel
from ..contracts.dappsys import DSToken
from ..contracts.PreimageManager import PreimageManager
from ..contracts.SpritesRegistry import SpritesRegistry
from ..contracts.SpritesEthRegistry import SpritesEthRegistry
from ..util import GAS, check_tx, deploy_contract, fund_account, generate_preimage, mint

GETH_URL = "http://localhost:8545"
PARTY_NAMES = ["alice", "bob"]

DEPLOYER = "0xd124b979f746be85706daa1180227e716eafcc5c"
ALICE = "0xa49aad37c34e92236690b93e291ae5f10daf7cbe"
BOB = "0xb357fc3dbd4cdb7cbd96aa0a0bd905dbe56cab77"
CHARLIE = "0xcBE431FF3fdcd4d735df5706e755D0f8726549f0"

DEPLOYER_PK = "0xe33292da27178504b848586dcee3011a7e21ee6ed96f9df17487fd6518a128c7"
ALICE_PK = "0xd8ae722d3a6876fd27907c434968e7373c6fbb985242e545a427531132ef3a71"
BOB_PK = "0x28e58f2f6a924d381e243ec1ca4a2239d2b35ebd9a44cec11aead6848a52630b"
CHARLIE_PK = "0x8e1733c6774268aee3db54901086b1f642f51e60300674ae3b33f1e1217ec7f5"

Account = namedtuple("Account", "address privateKey")

ACCOUNTS = {
    name: Account(to_checksum_address(address), private_key)
    for name, address, private_key in zip(
        ["deployer", "alice", "bob", "charlie"],
        [DEPLOYER, ALICE, BOB, CHARLIE],
        [DEPLOYER_PK, ALICE_PK, BOB_PK, CHARLIE_PK],
    )
}


@pytest.fixture(scope="session")
def web3():
    w3 = Web3(HTTPProvider(GETH_URL))

    # enable eth.account
    w3.eth.enable_unaudited_features()

    # for POA dev chain, see
    # https://web3py.readthedocs.io/en/latest/middleware.html#geth-style-proof-of-authority
    w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    return w3


# Account generation is slow, on the order of a second.
# We reuse the accounts for the entire session but use function scoped
# token contracts to make sure balances are zero initially.


@pytest.fixture
def mock_address():
    return eth_account.Account.create().address


@pytest.fixture(scope="session")
def guy(web3):
    return web3.eth.accounts[0]


@pytest.fixture(scope='session')
def tx_args(guy):
    return {'from': guy, 'gas': GAS}


def _get_account(web3, guy, name):
    account = ACCOUNTS[name]
    # web3.personal.unlockAccount(account.address, None)
    fund_account(web3, guy, account)
    return account


@pytest.fixture(scope="session")
def alice(web3, guy):
    return _get_account(web3, guy, "alice")


@pytest.fixture(scope="session")
def bob(web3, guy):
    return _get_account(web3, guy, "bob")


@pytest.fixture(scope="session")
def charlie(web3, guy):
    return _get_account(web3, guy, "charlie")


@pytest.fixture(scope="session")
def deployer(web3):
    return web3.eth.accounts[0]


@pytest.fixture(scope="session")
def registry(web3, deployer, preimage_manager):
    return deploy_contract(
        web3,
        deployer,
        "SpritesRegistry.sol",
        "SpritesRegistry",
        SpritesRegistry,
        args=[preimage_manager._contract.address],
    )


@pytest.fixture(scope="session")
def eth_registry(web3, deployer, preimage_manager):
    return deploy_contract(
        web3,
        deployer,
        "SpritesEthRegistry.sol",
        "SpritesEthRegistry",
        SpritesEthRegistry,
        args=[preimage_manager._contract.address],
    )


@pytest.fixture(scope="session")
def preimage_manager(web3, deployer):
    return deploy_contract(
        web3, deployer, "PreimageManager.sol", "PreimageManager", PreimageManager
    )


@pytest.fixture(scope="function")
def token(web3, deployer):
    token = deploy_contract(
        web3, deployer, "dappsys.sol", "DSToken", DSToken, args=[deployer]
    )
    mint(web3, token, deployer)
    return token


@pytest.fixture(scope="function")
def other_token(web3, deployer):
    return token(web3, deployer)


@pytest.fixture
def mock_channel(
    web3, mock_address, registry, preimage_manager, acting_party, other_party
):
    tx_hash = registry.createChannel(other_party.address, mock_address).transact(
        {"from": acting_party.address, "gas": GAS}
    )

    receipt = check_tx(web3, tx_hash)
    channel_id = web3.toInt(hexstr=receipt.logs[0].data)

    return Channel(
        web3,
        registry,
        preimage_manager,
        mock_address,
        channel_id,
        acting_party,
        other_party,
    )


@pytest.fixture
def channel(
    web3,
    token: DSToken,
    registry: SpritesRegistry,
    preimage_manager: PreimageManager,
    acting_party,
    other_party,
):
    tx_hash = registry.createChannel(
        other_party.address, token._contract.address
    ).transact(
        {"from": acting_party.address, "gas": GAS}
    )

    receipt = check_tx(web3, tx_hash)
    channel_id = web3.toInt(hexstr=receipt.logs[0].data)

    return Channel(
        web3, registry, preimage_manager, token, channel_id, acting_party, other_party
    )


@pytest.fixture
def eth_channel(
    web3,
    eth_registry: SpritesEthRegistry,
    preimage_manager: PreimageManager,
    acting_party,
    other_party,
):
    tx_hash = eth_registry.createChannel(
        other_party.address
    ).transact(
        {"from": acting_party.address, "gas": GAS}
    )

    receipt = web3.eth.getTransactionReceipt(tx_hash)
    channel_id = web3.toInt(hexstr=receipt.logs[0].data)

    return EthChannel(
        web3, eth_registry, preimage_manager, channel_id, acting_party, other_party
    )



@pytest.fixture(params=["alice", "bob"])
def acting_party_name(request):
    return request.param


@pytest.fixture
def acting_party(acting_party_name, alice, bob):
    return alice if acting_party_name == "alice" else bob


@pytest.fixture
def other_party_name(acting_party_name):
    return next(name for name in PARTY_NAMES if name != acting_party_name)


@pytest.fixture
def other_party(other_party_name, alice, bob):
    return alice if other_party_name == "alice" else bob


@pytest.fixture
def third_party(charlie):
    return charlie


@pytest.fixture
def preimage():
    return generate_preimage()


@pytest.fixture
def round():
    return 0


@pytest.fixture
def new_round():
    return 1


@pytest.fixture
def amount():
    return 0


@pytest.fixture
def new_amount():
    return 0


@pytest.fixture
def payment(amount):
    return Payment(amount=amount)


@pytest.fixture
def new_payment(new_amount):
    return Payment(amount=new_amount)


@pytest.fixture
def deposits():
    return [0, 0]


@pytest.fixture
def new_deposits(deposits):
    return deposits


@pytest.fixture
def credits():
    return [0, 0]


@pytest.fixture
def new_credits(credits):
    return credits


@pytest.fixture
def withdrawals():
    return [0, 0]


@pytest.fixture
def new_withdrawals(withdrawals):
    return withdrawals


@pytest.fixture
def new_state(new_deposits, new_credits, new_withdrawals, new_round, new_payment):
    return ChannelState(
        deposits=new_deposits,
        credits=new_credits,
        withdrawals=new_withdrawals,
        round=new_round,
        payment=new_payment,
    )


@pytest.fixture
def last_state(deposits, credits, withdrawals, round, payment):
    return ChannelState(
        deposits=deposits,
        credits=credits,
        withdrawals=withdrawals,
        round=round,
        payment=payment,
    )
