from crabpot.core.config import config
from crabpot.core.exceptions import EmptyPotNameError, ExistingPotNameError, InvalidPotNameError
from crabpot.core.pot import Pot
import re

def create_pot(name):
    if len(name.strip()) == 0:
        raise EmptyPotNameError

    if not re.match(r"^[A-Za-z0-9_]+$", name):
        raise InvalidPotNameError

    all_pots = get_pots()
    if name in all_pots:
        raise ExistingPotNameError

    pot = Pot(name)
    pot.create()

def get_pots():
    if not config.BASE_DIR.exists():
        return []

    return [p.name for p in config.BASE_DIR.iterdir() if p.is_dir()]

def create_crab(pot_name, crab_name):
    pass

