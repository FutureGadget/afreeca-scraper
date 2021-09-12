class NotOnAirException(Exception):
    def __init__(self):
        super().__init__("The BJ is not on air.")
