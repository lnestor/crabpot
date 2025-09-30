from click.testing import CliRunner
import crabpot
from crabpot.pot import Pot
from crabpot.cli import main
from crabpot.util import load_pot
import pytest
import subprocess
import os
from tests.factories import create_pot, create_crab

def test_submit_with_unsubmitted_crabs_submits_crabs(cmd_runner, create_pot, create_crab):
    pot = create_pot(name="mypot")
    crab = create_crab(pot)
    pot.save()

    runner = CliRunner()
    runner.invoke(main, args=["submit", "mypot"], catch_exceptions=False)

    assert len(cmd_runner.recv_cmds) == 1
    cmd, kwargs = cmd_runner.recv_cmds[0]
    assert cmd == "submit"
    assert kwargs["config"] == crab.get_crab_config()

    new_pot = load_pot("mypot")
    assert new_pot.get_crab(crab.name).status == "submitted"

def test_submit_with_single_crab_only_submits_that_crab(cmd_runner, create_pot, create_crab):
    pot = create_pot(name="mypot")
    crab1 = create_crab(pot)
    crab2 = create_crab(pot)
    pot.save()

    runner = CliRunner()
    runner.invoke(main, args=["submit", f"mypot.{crab2.name}"], catch_exceptions=False)

    assert len(cmd_runner.recv_cmds) == 1
    cmd, kwargs = cmd_runner.recv_cmds[0]
    assert cmd == "submit"
    assert kwargs["config"] == crab2.get_crab_config()

def test_submit_with_single_submitted_crab_exits_as_success(cmd_runner, create_pot, create_crab):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["submit", f"mypot.{crab.name}"], catch_exceptions=False)

    assert len(cmd_runner.recv_cmds) == 0

    assert result.exit_code == 0
    assert "no crab jobs to submit" in result.stdout.lower()

def test_submit_with_already_submitted_crabs_doesnt_submit_those_crabs(cmd_runner, create_pot, create_crab):
    pot = create_pot(name="mypot")
    create_crab(pot, status="submitted")
    create_crab(pot, status="submitted")
    pot.save()

    runner = CliRunner()
    runner.invoke(main, args=["submit", "sample"], catch_exceptions=False)

    assert len(cmd_runner.recv_cmds) == 0

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
