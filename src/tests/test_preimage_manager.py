import pytest

from ..util import generate_preimage

pytestmark = pytest.mark.usefixtures(
    "web3", "alice", "bob", "charlie", "acting_party", "other_party", "channel"
)


def test_preimage_manager(web3, channel, preimage_manager, acting_party):
    preimage = generate_preimage()
    channel.submit_preimage(who=acting_party, preimage=preimage)
    assert preimage_manager.revealedBefore(preimage, web3.eth.blockNumber)
