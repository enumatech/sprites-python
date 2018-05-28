class TransactionFailed(Exception):
    pass


class StateValidationError(Exception):
    pass


class InsufficientCredits(StateValidationError):
    pass


class Overpayment(StateValidationError):
    pass


class ForbiddenStateChange(StateValidationError):
    pass


class Overwithdrawal(ForbiddenStateChange):
    pass


class RoundNotAdvanced(ForbiddenStateChange):
    pass


class PaymentError(ForbiddenStateChange):
    pass


class BadSignature(Exception):
    pass
