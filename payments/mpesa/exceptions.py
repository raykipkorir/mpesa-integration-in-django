class MpesaError(Exception):
    """Raised when don't get api response"""

    def __init__(self, message: str):
        self.message = message
        super().__init__()
