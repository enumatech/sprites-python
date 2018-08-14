def test_preimage_manager(web3, channel, preimage_manager, acting_party, preimage):
    channel.submit_preimage(who=acting_party, preimage=preimage)
    assert preimage_manager.revealedBefore(preimage, web3.eth.blockNumber)
