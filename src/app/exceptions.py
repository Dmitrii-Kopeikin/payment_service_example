import abc


INTERNAL_SERVER_ERROR_MSG = "Internal server error"


class CustomError(Exception, metaclass=abc.ABCMeta):
    custom_message: str = ""

    def __init__(self, message: str | None = None):
        message = f"{self.custom_message}{': ' + message if message else "."}"
        super().__init__(message)


class UserExistsError(CustomError):
    custom_message = "User already exists"


class UserNotFoundError(CustomError):
    custom_message = "User not found"


class TransactionProcessedError(CustomError):
    custom_message = "Transaction already processed"


class TransactionNotFoundError(CustomError):
    custom_message = "Transaction not found"


class WrongTimeStampError(CustomError):
    custom_message = "Wrong timestamp. Are you from future?"


class AmountExceedsBalanceError(CustomError):
    custom_message = "Amount exceeds balance"


class TransactionExceedsBalanceError(CustomError):
    custom_message = "Transaction exceeds balance"
