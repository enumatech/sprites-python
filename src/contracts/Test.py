class Test:

    def __init__(self, contract):
        self._contract = contract

    def get(self):
        return self._contract.functions.get()

    def getArrays(self):
        return self._contract.functions.getArrays()

    def getStruct(self):
        return self._contract.functions.getStruct()

    def incr(self):
        return self._contract.functions.incr()
