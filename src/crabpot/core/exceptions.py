class PotNameError(Exception):
    pass

class EmptyPotNameError(PotNameError):
    pass

class ExistingPotNameError(PotNameError):
    pass

class InvalidPotNameError(PotNameError):
    pass
