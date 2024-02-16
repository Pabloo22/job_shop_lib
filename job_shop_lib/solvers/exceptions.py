class NoSolutionFound(Exception):
    """Exception raised when no solution is found."""

    def __init__(
        self, message="No solution could be found for the given problem"
    ):
        self.message = message
        super().__init__(self.message)
