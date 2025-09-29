import pytest
from pathlib import Path
from crabpot.pot import Pot
from crabpot.exceptions import MissingPotError
from crabpot.configuration import Config

def test_exists_on_disk_when_dir_exists_returns_true():
    Path(".crabpot/mypot").mkdir()

    pot = Pot("mypot")
    assert pot.exists_on_disk()

def test_exists_on_disk_when_dir_doesnt_exist_returns_false():
    pot = Pot("mypot")
    assert not pot.exists_on_disk()

def test_save_writes_dir():
    pot = Pot("mypot")
    pot.save()

    assert Path(".crabpot/mypot").exists()
    assert Path(".crabpot/mypot/pot.pkl").exists()

def test_create_crab_creates_a_crab_definition():
    pot = Pot("mypot")
    crab = pot.create_crab("crab")

    assert crab.name == "crab"
    assert crab in pot._crabs

def test_get_unsubmitted_crabs_returns_unsubmitted_crabs():
    pot = Pot("mypot")
    crab = pot.create_crab("unsubmitted_crab")
    
    result = pot.get_unsubmitted_crabs()

    assert len(result) == 1
    assert result[0] == crab


