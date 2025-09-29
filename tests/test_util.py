import click
import crabpot.util as util
import pytest
import subprocess
from crabpot.pot import Pot

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

def test_load_when_pot_doesnt_exist_throws_exception():
    new_pot = util.load_pot("mypot")

    assert new_pot is None
