import pytest
from pathlib import Path
from crabpot.pot import Pot
from crabpot.exceptions import MissingPotError, MissingTemplateError
from crabpot.configuration import Config

def test_exists_on_disk_when_dir_exists_returns_true():
    Path(".crabpot/mypot").mkdir()

    pot = Pot("mypot")
    assert pot.exists_on_disk()

def test_exists_on_disk_when_dir_doesnt_exist_returns_false():
    pot = Pot("mypot")
    assert not pot.exists_on_disk()

def test_save_writes_dir():
    Path(".crabpot").rmdir()

    pot = Pot("mypot")
    pot.save()

    assert Path(".crabpot/mypot").exists()
    assert Path(".crabpot/mypot/pot.pkl").exists()

def test_save_generates_crab_files(tmp_path):
    path = tmp_path / "crab_config.py.jinja"
    path.write_text("some text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path), is_crab_config=True)
    pot.save()

    with open(".crabpot/mypot/crab/crab_config.py") as f:
        contents = f.read()

    assert "some text" in contents

def test_save_when_missing_template_files_throws_error():
    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file("some_fake_path.py.jinja", is_crab_config=True)

    with pytest.raises(MissingTemplateError):
        pot.save()

    assert not Path(".crabpot/mypot").exists()

def test_create_crab_creates_a_crab_definition():
    pot = Pot("mypot")
    crab = pot.create_crab("crab")

    assert crab.name == "crab"
    assert crab in pot._crabs

def test_get_crabs_with_no_args_returns_all_crabs():
    pot = Pot("mypot")

    crab1 = pot.create_crab("crab1")
    crab2 = pot.create_crab("crab2")
    crab3 = pot.create_crab("crab3")

    result = pot.get_crabs()

    assert result == [crab1, crab2, crab3]

def test_get_crabs_with_status_returns_specific_crabs():
    pot = Pot("mypot")

    crab1 = pot.create_crab("crab1")
    crab1.status = "unsubmitted"

    crab2 = pot.create_crab("crab2")
    crab2.status = "submitted"

    crab3 = pot.create_crab("crab3")
    crab3.status = "finished"

    assert pot.get_crabs(status="unsubmitted") == [crab1]
    assert pot.get_crabs(status="submitted") == [crab2]
    assert pot.get_crabs(status="finished") == [crab3]
