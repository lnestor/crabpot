from crabpot.core.pot import Pot
from crabpot.core.config import config

def test_exists_when_pot_directory_exists_returns_true():
    pot = Pot("mypot")

    path = config.BASE_DIR / "mypot"
    path.mkdir(parents=True)

    assert pot.exists()

def test_exists_when_pot_directory_doesnt_exist_returns_false():
    pot = Pot("mypot")
    assert not pot.exists()

def test_create_makes_directory():
    pot = Pot("mypot")

    path = config.BASE_DIR / "mypot"
    assert not path.exists()

    pot.create()
    assert path.exists()
    assert path.is_dir()

def test_get_path_returns_directory():
    pot = Pot("mypot")
    assert pot.get_path() == config.BASE_DIR / "mypot"

def test_get_crab_returns_crab_object():
    pot = Pot("mypot")
    pot.create()
    pot.create_crab("mycrab")

    crab = pot.get_crab("mycrab")
    assert crab.name == "mycrab"

def test_get_crabs_returns_all_crabs():
    pot = Pot("mypot")
    pot.create()
    pot.create_crab("mycrab1")
    pot.create_crab("mycrab2")
    pot.create_crab("mycrab3")

    crabs = pot.get_crabs()
    assert len(crabs) == 3

    crab_names = [c.name for c in crabs]
    assert "mycrab1" in crab_names
    assert "mycrab2" in crab_names
    assert "mycrab3" in crab_names

def test_has_crab_when_has_crab_returns_true():
    pot = Pot("mypot")
    pot.create()

    pot.create_crab("mycrab")

    assert pot.has_crab("mycrab")

def test_has_crab_when_doesnt_have_crab_returns_false():
    pot = Pot("mypot")
    pot.create()

    assert not pot.has_crab("somecrab")

def test_create_crab_returns_crab_object():
    pot = Pot("mypot")
    pot.create()

    crab = pot.create_crab("mycrab")
    assert crab.name == "mycrab"

def test_eq_when_name_matches_returns_true():
    pot1 = Pot("mypot")
    pot2 = Pot("mypot")

    assert pot1 == pot2

def test_eq_when_name_doesnt_match_returns_false():
    pot1 = Pot("pot1")
    pot2 = Pot("pot2")

    assert pot1 != pot2
