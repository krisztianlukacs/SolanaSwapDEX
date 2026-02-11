class AppException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class InsufficientBalanceError(AppException):
    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(message, status_code=400)


class CooldownActiveError(AppException):
    def __init__(self, message: str = "Cooldown period active"):
        super().__init__(message, status_code=429)


class DailyLimitExceededError(AppException):
    def __init__(self, message: str = "Daily execution limit exceeded"):
        super().__init__(message, status_code=429)


class JupiterAPIError(AppException):
    def __init__(self, message: str = "Jupiter API error"):
        super().__init__(message, status_code=502)


class SlippageExceededError(AppException):
    def __init__(self, message: str = "Slippage exceeds maximum allowed"):
        super().__init__(message, status_code=400)
