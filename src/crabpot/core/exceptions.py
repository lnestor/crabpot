class CrabpotNameError(Exception):
    pass

class EmptyNameError(CrabpotNameError):
    pass

class ExistingNameError(CrabpotNameError):
    pass

class InvalidNameError(CrabpotNameError):
    pass

class MissingPotError(Exception):
    pass
