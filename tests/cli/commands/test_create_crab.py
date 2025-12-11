import pytest
from crabpot.cli.main import main
from crabpot.core import create_crab, create_pot
from click.testing import CliRunner

@pytest.fixture(autouse=True)
def precreate_pot():
    create_pot("mypot")

def test_cli_calls_create_crab(monkeypatch):
    calls = []
    def fake_create_crab(pot_name, crab_name):
        calls.append((pot_name, crab_name))
    monkeypatch.setattr("crabpot.core.create_crab", fake_create_crab)

    runner = CliRunner()
    runner.invoke(main, args=["create-crab", "mypot", "mycrab"])

    assert len(calls) == 1
    assert calls[0] == ("mypot", "mycrab")

def test_cli_returns_success():
    runner = CliRunner()
    result = runner.invoke(main, args=["create-crab", "mypot", "mycrab"])

    assert result.exit_code == 0
    assert result.output == "Successfully created crab \"mycrab\" in pot \"mypot\"\n"

def test_cli_when_empty_name_prints_message():
    runner = CliRunner()
    result = runner.invoke(main, args=["create-crab", "mypot", ""])

    assert result.exit_code != 0
    assert "cannot be blank" in result.output

def test_cli_when_invalid_name_prints_message():
    runner = CliRunner()
    result = runner.invoke(main, args=["create-crab", "mypot", "@#$@"])

    assert result.exit_code != 0
    assert "can only be alphanumeric characters and underscores" in result.output

def test_cli_when_existing_name_prints_message():
    create_crab("mypot", "mycrab")

    runner = CliRunner()
    result = runner.invoke(main, args=["create-crab", "mypot", "mycrab"])

    assert result.exit_code != 0
    assert "crab with name \"mycrab\" already exists in pot \"mypot\"" in result.output

def test_cli_when_pot_missing_prints_message():
    runner = CliRunner()
    result = runner.invoke(main, args=["create-crab", "missing", "mycrab"])

    assert result.exit_code != 0
    assert "cannot find pot \"missing\"" in result.output
