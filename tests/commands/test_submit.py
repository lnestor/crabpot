from click.testing import CliRunner
import crabpot
from crabpot.pot import Pot
from crabpot.cli import main
import pytest
import subprocess
import os

def test_submit_with_unsubmitted_crabs_submits_crabs(cmd_runner, tmp_path):
    crab_config_path = tmp_path / "crab_config.py.jinja"
    crab_config_path.write_text("{{ test }}")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(crab_config_path), is_crab_config=True)
    crab.substitutions = {"test": "testing dataset"}
    pot.save()

    runner = CliRunner()
    runner.invoke(main, args=["submit", "mypot"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 1
    cmd, kwargs = cmd_runner.received_commands[0]
    assert cmd == ["crab", "submit", "-c", ".crabpot/mypot/crab/crab_config.py"]

def test_submit_with_single_crab_only_submits_that_crab(cmd_runner, tmp_path):
    crab_config_path = tmp_path / "crab_config.py.jinja"
    crab_config_path.write_text("some file")

    pot = Pot("mypot")
    crab1 = pot.create_crab("crab1")
    crab1.add_template_file(str(crab_config_path), is_crab_config=True)

    crab2 = pot.create_crab("crab2")
    crab2.add_template_file(str(crab_config_path), is_crab_config=True)
    pot.save()

    runner = CliRunner()
    runner.invoke(main, args=["submit", "mypot.crab2"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 1
    cmd, kwargs = cmd_runner.received_commands[0]
    assert cmd == ["crab", "submit", "-c", ".crabpot/mypot/crab2/crab_config.py"]

def test_submit_with_single_crab_already_submitted_exits_as_success(cmd_runner, tmp_path):
    crab_config_path = tmp_path / "crab_config.py.jinja"
    crab_config_path.write_text("some file")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.status = "submitted"
    crab.add_template_file(str(crab_config_path), is_crab_config=True)
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["submit", "mypot.crab"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 0

    assert result.exit_code == 0
    assert "no crab jobs to submit" in result.stdout.lower()

def test_submit_with_already_submitted_crabs_doesnt_submit_those_crabs(cmd_runner, tmp_path):
    crab_config_path = tmp_path / "crab_config.py.jinja"
    crab_config_path.write_text("some text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(crab_config_path), is_crab_config=True)
    crab.status = "submitted"
    pot.save()

    runner = CliRunner()
    runner.invoke(main, args=["submit", "sample"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 0

def test_submit_with_no_crabs_exits_as_success():
    pot = Pot("sample")
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["submit", "sample"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "no crab jobs to submit" in result.stdout.lower()

def test_submit_when_pot_not_found_exits_as_failure():
    runner = CliRunner()
    result = runner.invoke(main, args=["submit", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "pot sample not found" in result.stdout.lower()

def test_with_no_cmsenv_exits_as_failure(set_valid_cmsenv):
    set_valid_cmsenv(False)

    runner = CliRunner()
    result = runner.invoke(main, args=["submit", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "cmsenv" in result.stdout.lower()

def test_with_no_grid_cert_exits_as_failure(set_valid_grid_cert):
    set_valid_grid_cert(False)

    runner = CliRunner()
    result = runner.invoke(main, args=["submit", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "grid certificate" in result.stdout.lower()
