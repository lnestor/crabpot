from crabpot.core.commands import create_pot, get_pots, create_crab, get_crabs
from crabpot.core.exceptions import EmptyNameError, ExistingNameError, InvalidNameError, MissingPotError
from crabpot.core.config import config
import pytest

def test_create_pot_creates_directory():
    create_pot("mypot")
    path = config.BASE_DIR / "mypot"
    assert path.exists()

def test_create_pot_with_empty_pot_name_throws_exception():
    with pytest.raises(EmptyNameError):
        create_pot("")

def test_create_pot_with_existing_pot_name_throws_exception():
    create_pot("mypot")

    with pytest.raises(ExistingNameError):
        create_pot("mypot")

def test_create_pot_with_invalid_name_throws_exception():
    with pytest.raises(InvalidNameError):
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

def test_create_crab_creates_directory():
    create_pot("mypot")
    create_crab("mypot", "mycrab")
    path = config.BASE_DIR / "mypot" / "mycrab"
    assert path.exists()

def test_create_crab_with_missing_pot_name_throws_exception():
    with pytest.raises(MissingPotError):
        create_crab("missing", "mycrab")

def test_create_crab_with_empty_crab_name_throws_exception():
    create_pot("mypot")
    with pytest.raises(EmptyNameError):
        create_crab("mypot", "")

def test_create_crab_with_invalid_crab_name_throws_exception():
    create_pot("mypot")
    with pytest.raises(InvalidNameError):
        create_crab("mypot", "@#$@")

def test_create_crab_with_exising_crab_name_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")
    with pytest.raises(ExistingNameError):
        create_crab("mypot", "mycrab")

def test_get_crabs_returns_all_crabs():
    create_pot("mypot")
    create_crab("mypot", "mycrab1")
    create_crab("mypot", "mycrab2")
    create_crab("mypot", "mycrab3")

    crabs = get_crabs("mypot")

    assert len(crabs) == 3
    assert "mycrab1" in crabs
    assert "mycrab2" in crabs
    assert "mycrab3" in crabs

def test_get_crab_when_no_crabs_returns_empty_array():
    create_pot("mypot")
    crabs = get_crabs("mypot")
    assert len(crabs) == 0

def test_get_crab_when_pot_doesnt_exist_throws_exception():
    with pytest.raises(MissingPotError):
        get_crabs("missing")
