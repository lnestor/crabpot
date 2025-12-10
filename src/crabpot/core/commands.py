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
    if name in [pot.name for pot in all_pots]:
        raise ExistingPotNameError

    pot = Pot(name)
    pot.create()
    return pot

def get_pots():
    if not config.BASE_DIR.exists():
        return []

    subpaths = [p.name for p in config.BASE_DIR.iterdir() if p.is_dir()]
    return [Pot(subpath) for subpath in subpaths]

