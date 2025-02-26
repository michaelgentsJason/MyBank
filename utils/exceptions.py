class BankException(Exception):
    """Base exception for all bank related errors"""
    pass

class ValidationError(BankException):
    """Raised when data validation fails"""
    pass

class InsufficientFundsError(BankException):
    """Raised when account has insufficient funds"""
    pass

class AccountNotFoundError(BankException):
    """Raised when account is not found"""
    pass

class TransactionError(BankException):
    """Raised when transaction processing fails"""
    pass

class SecurityError(BankException):
    """Raised when security related operations fail"""
    pass

class AuthenticationError(BankException):
    """Raised when authentication related operations fail"""
    pass