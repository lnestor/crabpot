import click
import crabpot.util as util
import pytest
import subprocess
from crabpot.pot import Pot
from tests.factories import create_pot, create_crab

class DummyCompletedProcess:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode

@pytest.fixture(autouse=True)
def replace_cert():
    pass

@pytest.mark.parametrize(
    "stdout,expected",
    [("", False), ("/some/CMSSW/base\n", True)]
)
def test_check_cmsenv_when_cmsenv_ran(monkeypatch, stdout, expected):
    def dummy(*args, **kwargs):
        return DummyCompletedProcess(stdout=stdout)

    monkeypatch.setattr(subprocess, "run", dummy)
    assert util.cert.check_cmsenv() == expected

@pytest.mark.parametrize(
        "stdout,expected",
        [("3600\n", True), ("0\n", False), ("NotANumber\n", False)]
)
def test_check_grid_cert(monkeypatch, stdout, expected):
    def dummy(*args, **kwargs):
        return DummyCompletedProcess(stdout=stdout, returncode=0)

    monkeypatch.setattr(subprocess, "run", dummy)
    assert util.cert.check_grid_cert() == expected

def test_check_grid_cert_missing_voms_binary_throws_exception(monkeypatch):
    def dummy(*args, **kwargs):
        raise FileNotFoundError("voms-proxy-info not found")

    monkeypatch.setattr(subprocess, "run", dummy)

    with pytest.raises(click.ClickException) as e:
        util.cert.check_grid_cert()

    assert "voms-proxy-info" in str(e.value)

def test_load_pot_when_pot_exists_returns_pot():
    pot = Pot("mypot")
    pot.save()

    new_pot = util.load_pot("mypot")
    assert new_pot.name == "mypot"

def test_load_when_pot_doesnt_exist_returns_none():
    new_pot = util.load_pot("mypot")

    assert new_pot is None

class GetCrabsFromTarget:
    class WithPotTarget:
        def test_with_missing_pot_throws_exception(self):
            from crabpot.exceptions import MissingPotError

            with pytest.raises(MissingPotError):
                util.get_crabs_from_target("nonexistent")

        def test_without_filter_returns_all_crabs(self, create_pot, create_crab):
            pot = create_pot(name="mypot")
            crab1 = create_crab(pot, status="submitted")
            crab2 = create_crab(pot, status="unsubmitted")
            pot.save()

            returned_pot, crabs = util.get_crabs_from_target("mypot")

            assert returned_pot.name == "mypot"
            assert len(crabs) == 2
            assert crabs[0].name == crab1.name
            assert crabs[1].name == crab2.name

        def test_with_filter_returns_filtered_crabs(self, create_pot, create_crab):
            pot = create_pot(name="mypot")
            crab1 = create_crab(pot, status="submitted")
            crab2 = create_crab(pot, status="unsubmitted")
            pot.save()

            returned_pot, crabs = util.get_crabs_from_target("mypot", status="submitted")

            assert returned_pot.name == "mypot"
            assert len(crabs) == 1
            assert crabs[0].status == "submitted"

    class WithCrabTarget:
        def test_with_missing_pot_throws_exception(self):
            from crabpot.exceptions import MissingPotError

            with pytest.raises(MissingPotError):
                util.get_crabs_from_target("nonexistentpot.crab")

        def test_with_missing_crab_throws_exception(self, create_pot):
            from crabpot.exceptions import MissingCrabError

            pot = craete_pot(name="mypot")
            pot.save()

            with pytest.raises(MissingCrabError):
                util.get_crabs_from_target("mypot.crab")

        def test_without_filter_returns_crab(self, create_pot, create_crab):
            pot = create_pot(name="mypot")
            crab1 = create_crab(pot, status="submitted")
            crab2 = create_crab(pot, status="unsubmitted")
            pot.save()

            returned_pot, crabs = util.get_crabs_from_target(f"mypot.{crab1.name}")

            assert returned_pot.name == "mypot"
            assert len(crabs) == 1
            assert crabs[0].name == crab1.name

        def test_with_filter_when_crab_passes_filter_returns_crab(self, create_pot, create_crab):
            pot = create_pot(name="mypot")
            crab1 = create_crab(pot, status="submitted")
            crab2 = create_crab(pot, status="unsubmitted")
            pot.save()

            returned_pot, crabs = util.get_crabs_from_target(f"mypot.{crab1.name}", status="submitted")

            assert returned_pot.name == "mypot"
            assert len(crabs) == 1
            assert crabs[0].name == crab1.name

        def test_with_filter_when_crab_fails_filter_returns_no_crab(self, create_pot, create_crab):
            pot = create_pot(name="mypot")
            crab1 = create_crab(pot, status="submitted")
            crab2 = create_crab(pot, status="unsubmitted")
            pot.save()

            returned_pot, crabs = util.get_crabs_from_target(f"mypot.{crab1.name}", status="unsubmitted")

            assert returned_pot.name == "mypot"
            assert len(crabs) == 0

