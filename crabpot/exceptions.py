class CrabpotError(Exception):
    pass

class DuplicatePotError(CrabpotError):
    def __init__(self, message="Attempted to create pot that already exists"):
        super().__init__(message)

class InvalidConfigError(CrabpotError):
    pass

class MissingPotError(CrabpotError):
    pass

class MissingTemplateError(CrabpotError):
    pass
