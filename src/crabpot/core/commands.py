from crabpot.core.config import config
from crabpot.core.exceptions import EmptyNameError, ExistingNameError, InvalidNameError, MissingCrabError, MissingTemplateError, DuplicateTemplateError, MissingPotError
from crabpot.core.pot import Pot
import re
import shutil
import pathlib

def _pot_exists(pot_name):
    all_pots = get_pots()
    return pot_name in all_pots

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
    if not _pot_exists(pot_name):
        raise MissingPotError

    if len(crab_name.strip()) == 0:
        raise EmptyNameError

    if not re.match(r"^[A-Za-z0-9_]+$", crab_name):
        raise InvalidNameError

    pot = Pot(pot_name)

    if pot.has_crab(crab_name):
        raise ExistingNameError

    pot.create_crab(crab_name)

def get_crabs(pot_name):
    if not _pot_exists(pot_name):
        raise MissingPotError

    pot = Pot(pot_name)
    return [crab.name for crab in pot.get_crabs()]

def add_template_file(pot_name, crab_name, template_path_str):
    if not _pot_exists(pot_name):
        raise MissingPotError

    template_path = pathlib.Path(template_path_str)
    if not template_path.exists():
        raise MissingTemplateError

    pot = Pot(pot_name)

    if not pot.has_crab(crab_name):
        raise MissingCrabError

    crab = pot.get_crab(crab_name)

    if crab.has_template_file(template_path.name):
        raise DuplicateTemplateError

    crab.add_template(template_path)

def add_substitution(pot_name, crab_name, key, value):
    if len(key.strip()) == 0:
        raise ValueError

    if len(value.strip()) == 0:
        raise ValueError

    if not _pot_exists(pot_name):
        raise MissingPotError

    pot = Pot(pot_name)

    if not pot.has_crab(crab_name):
        raise MissingCrabError

    crab = pot.get_crab(crab_name)
    crab.add_substitution(key, value)

def generate(pot_name, crab_name):
    if not _pot_exists(pot_name):
        raise MissingPotError

    pot = Pot(pot_name)

    if not pot.has_crab(crab_name):
        raise MissingCrabError

    crab = pot.get_crab(crab_name)
    crab.generate()
