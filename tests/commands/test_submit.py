from click.testing import CliRunner
from crabpot.pot import Pot
from crabpot.cli import main
from crabpot.util import load_pot
import pytest
from tests.factories import create_pot, create_crab

SUCCESS_RESPONSE = [
    "Finished importing CMSSW configuration some/path/to/cmssw_pset_cfg.py",
    "Sending the request to the server at cmsweb.cern.ch",
    "Success: Your task has been delivered to the prod CRAB3 server.",
    "Task name: 251003_194836:username_crab_TestRequest",
    "Project dir: some/path/crab_TestRequest",
    "Please use ' crab status -d some/path/crab_TestRequest ' to check how the submission process proceeds.",
    "Log file is /some/path/to/log/file/crab.log",
]

FAILURE_RESPONSE = [
    "Working area crab_some_request already exists ",
    "Please change the requestName in the config file"
]

class TestWithPotTarget:
    @pytest.fixture
    def pot(self, create_pot, create_crab):
        pot = create_pot(name="mypot")
        crab1 = create_crab(pot, status="unsubmitted")
        crab2 = create_crab(pot, status="unsubmitted")
        crab3 = create_crab(pot, status="submitted")
        crab4 = create_crab(pot, status="submitted")
        pot.save()
        return pot

    def test_submit_calls_crab_submit_on_unsubmitted_crabs(self, pot, fp):
        unsub_crabs = pot.get_crabs(status="unsubmitted")
        sub_crabs = pot.get_crabs(status="submitted")

        fp.register(["crab", "submit", fp.any()], stdout=SUCCESS_RESPONSE)
        fp.keep_last_process(True)

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "mypot"])
        assert result.exit_code == 0

        for crab in unsub_crabs:
            assert ["crab", "submit", crab.get_crab_config()] in fp.calls

        for crab in sub_crabs:
            assert not ["crab", "submit", crab.get_crab_config()] in fp.calls

    def test_submit_when_successful_sets_status_to_submitted(self, pot, fp):
        unsub_crabs = pot.get_crabs(status="unsubmitted")

        fp.register(["crab", "submit", fp.any()], stdout=SUCCESS_RESPONSE)
        fp.keep_last_process(True)

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "mypot"])
        assert result.exit_code == 0

        new_pot = load_pot("mypot")
        for name in [c.name for c in unsub_crabs]:
            assert new_pot.get_crab(name).status == "submitted"

    def test_submit_when_failure_doesnt_change_status(self, pot, fp):
        unsub_crabs = pot.get_crabs(status="unsubmitted")

        fp.register(["crab", "submit", fp.any()], stdout=FAILURE_RESPONSE)
        fp.keep_last_process(True)

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "mypot"])
        assert result.exit_code == 0

        new_pot = load_pot("mypot")
        for name in [c.name for c in unsub_crabs]:
            assert new_pot.get_crab(name).status == "unsubmitted"

    def test_submit_when_failure_processes_later_crabs_normally(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab1 = create_crab(pot, status="unsubmitted")
        crab2 = create_crab(pot, status="unsubmitted")
        pot.save()

        fp.register(["crab", "submit", fp.any()], stdout=FAILURE_RESPONSE)
        fp.register(["crab", "submit", fp.any()], stdout=SUCCESS_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "mypot"])
        assert result.exit_code == 0

        new_pot = load_pot("mypot")
        assert new_pot.get_crab(crab2.name).status == "submitted"

    def test_submit_when_incorrect_pot_name_exits_as_failure(self, pot):
        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "somepot"])

        assert result.exit_code != 0
        assert "pot somepot not found" in result.stdout.lower()

    def test_submit_when_no_unsubmitted_crabs_exits_as_failure(self, create_pot, create_crab):
        pot = create_pot("mypot")
        create_crab(pot, status="submitted")
        create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "mypot"])

        assert result.exit_code != 0
        assert "no crab jobs to submit" in result.stdout.lower()

    def test_submit_with_empty_pot_exits_as_failure(self, create_pot):
        pot = create_pot("mypot")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", "mypot"])

        assert result.exit_code != 0
        assert "pot mypot is empty" in result.stdout.lower()

class TestWithCrabTarget:
    def test_submit_when_crab_unsubmitted_calls_crab_submit(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="unsubmitted")
        pot.save()

        fp.register(["crab", "submit", fp.any()], stdout=SUCCESS_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", f"mypot.{crab.name}"])

        assert result.exit_code == 0
        assert ["crab", "submit", crab.get_crab_config()] in fp.calls

    def test_submit_when_crab_unsubmitted_sets_status_to_submitted(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="unsubmitted")
        pot.save()

        fp.register(["crab", "submit", fp.any()], stdout=SUCCESS_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", f"mypot.{crab.name}"])
        assert result.exit_code == 0

        new_pot = load_pot("mypot")
        assert new_pot.get_crab(crab.name).status == "submitted"

    def test_submit_when_crab_already_submitted_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", f"mypot.{crab.name}"])

        assert result.exit_code != 0
        assert f"crab {crab.name} is already submitted" in result.stdout.lower()

    def test_submit_when_incorrect_pot_name_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", f"otherpot.{crab.name}"])

        assert result.exit_code != 0
        assert "pot otherpot not found" in result.stdout.lower()

    def test_submit_when_incorrect_crab_name_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["submit", f"mypot.some_other_name"])

        assert result.exit_code != 0
        assert f"crab some_other_name not found in pot mypot" in result.stdout.lower()

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
