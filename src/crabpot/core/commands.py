from crabpot.core.config import config
from crabpot.core.exceptions import EmptyNameError, ExistingNameError, InvalidNameError
from crabpot.core.pot import Pot
import re

def create_pot(name):
    if len(name.strip()) == 0:
        raise EmptyNameError

    if not re.match(r"^[A-Za-z0-9_]+$", name):
        raise InvalidNameError

    all_pots = get_pots()
    if name in all_pots:
        raise ExistingNameError

    pot = Pot(name)
    pot.create()

def get_pots():
    if not config.BASE_DIR.exists():
        return []

    return [p.name for p in config.BASE_DIR.iterdir() if p.is_dir()]

def create_crab(pot_name, crab_name):
    pot = Pot.load(pot_name)

    if len(crab_name.strip()) == 0:
        raise EmptyNameError

    if not re.match(r"^[A-Za-z0-9_]+$", crab_name):
        raise InvalidNameError

    all_crabs = get_crabs(pot_name)
    if crab_name in all_crabs:
        raise ExistingNameError

    crab = pot.create_crab(crab_name)

def get_crabs(pot_name):
    pot = Pot.load(pot_name)
    return pot.get_crabs()
