class InvalidPixelValueError(Exception):
    """Exception raised when a pixel value is out of range."""

    pass


class NotFiniteValueError(Exception):
    """Exception raised when a value is not finite."""

    pass


class MissingEnvironmentVariableError(Exception):
    """Exception raised when an expected environment variable is missing."""

    pass


class ImageProcessingError(Exception):
    """Exception raised when an error occurs during image processing."""

    pass


class DatabaseCreationError(Exception):
    """Exception raised when an error occurs during database or table creation."""

    pass


class DatabaseConnectionError(Exception):
    """Exception raised when an error occurs during database connection."""

    pass


class DatabaseQueryError(Exception):
    """Exception raised when an error occurs during database query."""

    pass


class DataCleanerError(Exception):
    """Exception raised for errors in the DataCleaner class."""

    pass


class DatabaseServiceError(Exception):
    """Exception raised for errors in the DatabaseService class."""

    pass


class ColorMapError(Exception):
    """Exception raised for errors in the ColorMap class."""

    pass
