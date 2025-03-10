class UserNotFoundException(Exception):
    """Exception raised when a user is not found."""

    pass


class EmailAlreadyExistsException(Exception):
    """Exception raised when an email already exists."""

    pass
