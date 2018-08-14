class PreimageManager:
    def __init__(self, contract):
        self._contract = contract

    def revealedBefore(self, h, T):
        return self._contract.functions.revealedBefore(h, T)

    def submitPreimage(self, x):
        return self._contract.functions.submitPreimage(x)
