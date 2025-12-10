from crabpot.core.commands import create_pot, get_pots
from crabpot.core.exceptions import EmptyPotNameError, ExistingPotNameError, InvalidPotNameError
from crabpot.core.config import config
import pytest

def test_create_pot_creates_directory():
    create_pot("mypot")
    path = config.BASE_DIR / "mypot"
    assert path.exists()

def test_create_pot_with_empty_pot_name_throws_exception():
    with pytest.raises(EmptyPotNameError):
        create_pot("")

def test_create_pot_with_existing_pot_name_throws_exception():
    create_pot("mypot")

    with pytest.raises(ExistingPotNameError):
        create_pot("mypot")

def test_create_pot_with_invalid_name_throws_exception():
    with pytest.raises(InvalidPotNameError):
        create_pot(".. !@#$%")

def test_get_pots_returns_all_pots():
    create_pot("pot1")
    create_pot("pot2")
    create_pot("pot3")

    pots = get_pots()

    assert len(pots) == 3
    assert "pot1" in pots
    assert "pot2" in pots
    assert "pot3" in pots

def test_get_pots_when_base_dir_doesnt_exist_returns_empty_list():
    pots = get_pots()
    assert len(pots) == 0

