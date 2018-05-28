class PreimageManager:

    def __init__(self, contract):
        self._contract = contract

    def revealedBefore(self, h, T):
        return self._contract.functions.revealedBefore(h, T)

    def submitPreimage(self, x):
        return self._contract.functions.submitPreimage(x)


class SpriteChannel:

    def __init__(self, contract):
        self._contract = contract

    def amount(self):
        return self._contract.functions.amount()

    def credits(self, arg):
        return self._contract.functions.credits(arg)

    def deposit(self):
        return self._contract.functions.deposit()

    def deposits(self, arg):
        return self._contract.functions.deposits(arg)

    def expiry(self):
        return self._contract.functions.expiry()

    def finalize(self):
        return self._contract.functions.finalize()

    def hash(self):
        return self._contract.functions.hash()

    def players(self, arg):
        return self._contract.functions.players(arg)

    def sha3int(self, r):
        return self._contract.functions.sha3int(r)

    def status(self):
        return self._contract.functions.status()

    def trigger(self):
        return self._contract.functions.trigger()

    def update(self, sig, r, _credits, _withdrawals, _hash, _expiry, _amount):
        return self._contract.functions.update(sig, r, _credits,
            _withdrawals, _hash, _expiry, _amount)

    def verifySignature(self, pub, h, v, r, s):
        return self._contract.functions.verifySignature(pub, h, v, r, s)

    def withdraw(self):
        return self._contract.functions.withdraw()

    def withdrawals(self, arg):
        return self._contract.functions.withdrawals(arg)

    def withdrawn(self, arg):
        return self._contract.functions.withdrawn(arg)
