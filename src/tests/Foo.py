class Foo:
    def __init__(self, contract):
        self._contract = contract

    def bar(self, a):
        return self._contract.functions.bar(a)
