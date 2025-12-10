import pytest
from crabpot.cli.main import main
from crabpot.core.commands import create_pot
from click.testing import CliRunner

def test_cli_calls_create_pot(monkeypatch):
    calls = []
    def fake_create_pot(name):
        calls.append(name)
    monkeypatch.setattr("crabpot.core.commands.create_pot", fake_create_pot)

    runner = CliRunner()
    runner.invoke(main, args=["create-pot", "mypot"])

    assert len(calls) == 1
    assert calls[0] == "mypot"

def test_cli_returns_success(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(main, args=["create-pot", "mypot"])

    assert result.exit_code == 0
    assert result.output == "Successfully created pot \"mypot\"\n"

def test_cli_when_empty_name_prints_message(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(main, args=["create-pot", ""])

    assert result.exit_code != 0
    assert "cannot be blank" in result.output

def test_cli_when_invalid_name_prints_message(monkeypatch):
    runner = CliRunner()
    result = runner.invoke(main, args=["create-pot", "@#$@"])

    assert result.exit_code != 0
    assert "can only be alphanumeric characters and underscores" in result.output

def test_cli_when_existing_name_prints_message(monkeypatch):
    create_pot("mypot")

    runner = CliRunner()
    result = runner.invoke(main, args=["create-pot", "mypot"])

    assert result.exit_code != 0
    assert "pot with name \"mypot\" already exists" in result.output
