class PreimageManager:

    def __init__(self, contract):
        self._contract = contract

    def revealedBefore(self, h, T):
        return self._contract.functions.revealedBefore(h, T)

    def submitPreimage(self, x):
        return self._contract.functions.submitPreimage(x)


class SpritesRegistry:

    def __init__(self, contract):
        self._contract = contract

    def channels(self, arg):
        return self._contract.functions.channels(arg)

    def createChannel(self, other, tokenAddress):
        return self._contract.functions.createChannel(other, tokenAddress)

    def deposit(self, channelID, amount):
        return self._contract.functions.deposit(channelID, amount)

    def finalize(self, channelID):
        return self._contract.functions.finalize(channelID)

    def getDeadline(self, channelID):
        return self._contract.functions.getDeadline(channelID)

    def getDeposit(self, channelID):
        return self._contract.functions.getDeposit(channelID)

    def getState(self, channelID):
        return self._contract.functions.getState(channelID)

    def getStatus(self, channelID):
        return self._contract.functions.getStatus(channelID)

    def getWithdrawn(self, channelID):
        return self._contract.functions.getWithdrawn(channelID)

    def isSignatureOkay(self, pub, messageHash, sig):
        return self._contract.functions.isSignatureOkay(pub, messageHash, sig)

    def recoverAddress(self, messageHash, sig):
        return self._contract.functions.recoverAddress(messageHash, sig)

    def sha3int(self, r):
        return self._contract.functions.sha3int(r)

    def trigger(self, channelID):
        return self._contract.functions.trigger(channelID)

    def update(self, channelID, sig, credits, withdrawals, round,
        preimageHash, recipient, amount, expiry):
        return self._contract.functions.update(channelID, sig, credits,
            withdrawals, round, preimageHash, recipient, amount, expiry)

    def verifyUpdate(self, channelID, sig, credits, withdrawals, round,
        preimageHash, recipient, amount, expiry):
        return self._contract.functions.verifyUpdate(channelID, sig,
            credits, withdrawals, round, preimageHash, recipient, amount,
            expiry)

    def withdraw(self, channelID):
        return self._contract.functions.withdraw(channelID)
