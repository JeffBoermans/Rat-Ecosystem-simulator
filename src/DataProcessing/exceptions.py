class InputException(Exception):
    """A general exception to indicate that the input session
    file is malformed.
    """
    pass


class MissingInputKey(InputException):
    """A required key is missing from the input session file.
    """
    pass

class WrongInputFile(InputException):
    """The input file is not in the .json format.
    """
    pass

class SimulationException(Exception):
    """A general exception to indicate that the simulation is
    invalid/inconsistent.
        """
    pass

class InvalidAge(SimulationException):
    """A general exception to indicate that the simulation is
    invalid.
        """
    pass