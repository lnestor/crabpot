import pytest
from click.testing import CliRunner
from tests.factories import create_pot, create_crab
from crabpot.cli import main
from pathlib import Path
from crabpot import util

def test_reset_with_submitted_crab_sets_status_to_submitted(create_pot, create_crab):
    pot = create_pot("mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    assert crab.status == "submitted"
    assert Path(crab.get_base_crab_dir()).exists()

    runner = CliRunner()
    runner.invoke(main, args=["reset", f"mypot.{crab.name}"], catch_exceptions=False)

    new_pot = util.load_pot("mypot")
    new_crab = new_pot.get_crab(crab.name)

    assert new_crab.status == "unsubmitted"
    assert not Path(new_crab.get_base_crab_dir()).exists()

def test_reset_when_pot_not_found_exits_as_failure():
    runner = CliRunner()
    result = runner.invoke(main, args=["reset", f"mypot.crab"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "pot mypot not found" in result.stdout.lower()

def test_reset_with_missing_crab_exits_as_failure(create_pot, create_crab):
    pot = create_pot("mypot")
    crab = create_crab(pot)
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["reset", f"mypot.some_crab_name"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "crab some_crab_name not found" in result.stdout.lower()
