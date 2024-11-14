class AnalyticsError(Exception):
    """Base exception for errors in the file-processing-analytics library."""

class InvalidInputError(AnalyticsError):
    """
    Exception raised for invalid input to the analytics processor.

    This may occur if an unsupported type or improperly formatted input is provided.
    """

class ProcessingInterruptedError(AnalyticsError):
    """
    Exception raised when file processing is interrupted.

    This error can be used to handle interruptions or unexpected stops in the processing workflow.
    """
