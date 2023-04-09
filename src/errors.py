"""
This module defines exception classes.
"""

class NotOnAirException(Exception):
    """
    This is an Exception class that indicates the the target bj is not on air.
    """
    def __init__(self):
        super().__init__("The BJ is not on air.")
