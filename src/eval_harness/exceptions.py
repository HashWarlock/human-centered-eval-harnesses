"""Domain-specific exceptions for the eval harness package."""


class DatasetValidationError(ValueError):
    """Raised when a dataset record cannot be parsed or validated."""


class DuplicateCaseIDError(DatasetValidationError):
    """Raised when a dataset contains duplicate case identifiers."""


class ReportGenerationError(RuntimeError):
    """Raised when a report cannot be written to disk."""
