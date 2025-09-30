from click.testing import CliRunner
from crabpot.cli import main
from tests.factories import create_pot, create_crab

def test_info_prints_crab_statuses(create_pot, create_crab):
    pot = create_pot(name="mypot")
    create_crab(pot, status="submitted")
    create_crab(pot, status="unsubmitted")
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["info", "mypot"], catch_exceptions=False)

    assert "Number of crabs: 2" in result.stdout
    assert "Unsubmitted: 1" in result.stdout
    assert "Submitted: 1" in result.stdout

def test_info_verbose_prints_info_about_each_frab(create_pot, create_crab):
    pot = create_pot(name="mypot")
    create_crab(pot, status="submitted")
    create_crab(pot, status="unsubmitted")
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["info", "mypot", "--v"], catch_exceptions=False)

    assert "status: unsubmitted" in result.stdout.lower()
    assert "status: submitted" in result.stdout.lower()

    for crab in pot.get_crabs():
        assert crab.name in result.stdout

def test_info_with_missing_pot_exits_as_failure():
    runner = CliRunner()
    result = runner.invoke(main, args=["info", "mypot"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "pot mypot not found" in result.stdout.lower()
