class CrabpotError(Exception):
    pass

class DuplicatePotError(CrabpotError):
    def __init__(self, message="Attempted to create pot that already exists"):
        super().__init__(message)

class InvalidConfigError(CrabpotError):
    pass

class MissingPotError(CrabpotError):
    def __init__(self, pot_name):
        self.pot_name = pot_name
        super().__init__(f"Pot {pot_name} not found.")

class MissingCrabError(CrabpotError):
    def __init__(self, pot, crab_name):
        self.pot = pot
        self.crab_name = crab_name
        self.pot_name = pot.name
        super().__init__(f"Crab {crab_name} not found in pot {pot.name}")
