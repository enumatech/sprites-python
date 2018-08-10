class Application:

    def __init__(self, contract):
        self._contract = contract

    def transition(self, creditsA, creditsB, signers, cmds, inputs):
        return self._contract.functions.transition(creditsA, creditsB,
            signers, cmds, inputs)


class StateChannel:

    def __init__(self, contract):
        self._contract = contract

    def app(self):
        return self._contract.functions.app()

    def bestRound(self):
        return self._contract.functions.bestRound()

    def cmds(self, arg):
        return self._contract.functions.cmds(arg)

    def deadline(self):
        return self._contract.functions.deadline()

    def disputeLength(self):
        return self._contract.functions.disputeLength()

    def getDispute(self, i):
        return self._contract.functions.getDispute(i)

    def hstate(self):
        return self._contract.functions.hstate()

    def input(self, _cmd, _input):
        return self._contract.functions.input(_cmd, _input)

    def inputs(self, arg):
        return self._contract.functions.inputs(arg)

    def latestClaim(self):
        return self._contract.functions.latestClaim()

    def players(self, arg):
        return self._contract.functions.players(arg)

    def resolve(self, _creditsA, _creditsB, _r):
        return self._contract.functions.resolve(_creditsA, _creditsB, _r)

    def setstate(self, sigs, _i, _hstate):
        return self._contract.functions.setstate(sigs, _i, _hstate)

    def signers(self, arg):
        return self._contract.functions.signers(arg)

    def status(self):
        return self._contract.functions.status()

    def t_start(self):
        return self._contract.functions.t_start()

    def triggerdispute(self, sig):
        return self._contract.functions.triggerdispute(sig)

    def verifySignature(self, pub, h, v, r, s):
        return self._contract.functions.verifySignature(pub, h, v, r, s)
