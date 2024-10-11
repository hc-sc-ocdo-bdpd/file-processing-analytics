# file_processing_analytics/errors.py

class AnalyticsError(Exception):
    """Base exception for the analytics library."""

class InvalidInputError(AnalyticsError):
    """Invalid input provided."""

class ProcessingInterruptedError(AnalyticsError):
    """Processing was interrupted."""
