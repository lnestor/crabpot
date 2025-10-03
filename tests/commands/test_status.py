import pytest
from click.testing import CliRunner
from crabpot.cli import main
from crabpot.pot import Pot
from crabpot.util import load_pot
from tests.factories import create_pot, create_crab
import re

def get_status_output(
    submitted=0,
    running=0,
    transferring=0,
    failed=0,
    finished=0
):
    total = submitted + running + transferring + failed + finished

    result = """
Rucio client intialized for account myaccount
CRAB project directory:         /some/path/.crabpot/mypot/crab
Task name:                      250924_173012:my_crab_request
Grid scheduler - Task Worker:   crab3@vocms0121.cern.ch - crab-prod-tw01
Status on the CRAB server:      SUBMITTED
Task URL to use for HELP:       https://cmsweb.cern.ch/crabserver/ui/task/250924_173012%3Amy_crab_request
Dashboard monitoring URL:       https://monit-grafana.cern.ch/d/cmsTMDetail/cms-task-monitoring-task-view?orgId=11&var-user=myusername&var-task=250924_173012%3Amy_crab_request
Status on the scheduler:        COMPLETED

"""

    order = [submitted, running, transferring, failed, finished]
    labels = ["submitted", "running", "transferring", "failed", "finished"]

    has_done_first_line = False
    for idx, val in enumerate(order):
        percentage = val / total
        if val > 0 and not has_done_first_line:
            has_done_first_line = True
            result += f"Jobs status:                    {labels[idx].ljust(15)}{percentage * 100:.1f}%  ({str(val).rjust(2)}/{total})\n"
        elif val > 0:
            result += f"                                {labels[idx].ljust(15)}{percentage * 100:.1f}%  ({str(val).rjust(2)}/{total})\n"

    result += """
Summary of run jobs:
 * Memory: 86MB min, 3083MB max, 1192MB ave
 * Runtime: 0:01:03 min, 0:15:59 max, 0:04:11 ave
 * CPU eff: 11% min, 80% max, 53% ave
 * Waste: 989:45:01 (81% of total)

Log file is /some/path/.crabpot/mypot/crab/crab.log
    """
    return result

class TestWithPotTarget:
    def test_status_calls_crab_status_on_submitted_crabs(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab1 = create_crab(pot, status="unsubmitted")
        crab2 = create_crab(pot, status="submitted")
        crab3 = create_crab(pot, status="submitted")
        crab4 = create_crab(pot, status="finished")
        pot.save()

        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(submitted=10))
        fp.keep_last_process(True)

        runner = CliRunner()
        result = runner.invoke(main, args=["status", "mypot"])
        assert result.exit_code == 0

        assert fp.call_count(["crab", "status", "-d", fp.any()]) == 2
        assert ["crab", "status", "-d", crab2.get_crab_request_dir()] in fp.calls
        assert ["crab", "status", "-d", crab3.get_crab_request_dir()] in fp.calls

    def test_status_with_incorrect_pot_name_exits_as_failure(self):
        runner = CliRunner()
        result = runner.invoke(main, args=["status", "somepot"])

        assert result.exit_code != 0
        assert "pot somepot not found"

    def test_status_when_unexpected_error_continues_reading_later_crabs(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab1 = create_crab(pot, status="submitted")
        crab2 = create_crab(pot, status="submitted")
        pot.save()

        def stub_raise(process):
            raise

        fp.register(["crab", "status", "-d", fp.any()], callback=stub_raise)
        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(submitted=10, running=20, failed=30))

        runner = CliRunner()
        result = runner.invoke(main, args=["status", "mypot"])
        assert result.exit_code == 0

        assert f"Unexpected error" in result.stdout
        assert re.search(f"{crab2.name}\\s*Submitted: 10, Running: 20, Transferring: 0, Finished: 0, Failed: 30", result.stdout)

class TestWithCrabTarget:
    def test_status_when_crab_submitted_calls_crab_status(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        crab_other = create_crab(pot, status="submitted")
        pot.save()

        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(submitted=10))

        runner = CliRunner()
        result = runner.invoke(main, args=["status", f"mypot.{crab.name}"])
        assert result.exit_code == 0

        assert fp.call_count(["crab", "status", "-d", fp.any()]) == 1
        assert ["crab", "status", "-d", crab.get_crab_request_dir()] in fp.calls

    def test_status_when_incorrect_pot_name_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["status", f"otherpot.{crab.name}"])

        assert result.exit_code != 0
        assert f"pot otherpot not found" in result.stdout.lower()

    def test_status_when_incorrect_crab_name_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["status", "mypot.othercrab"])

        assert result.exit_code != 0
        assert f"crab othercrab not found" in result.stdout.lower()

def test_status_when_unsubmitted_prints_message(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="unsubmitted")
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"])

    assert result.exit_code == 0
    assert re.search(f"{crab.name}\\s*Unsubmitted", result.stdout)

def test_status_when_submitted_prints_job_summary(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=10, transferring=5, finished=10, failed=5))

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"])
    assert result.exit_code == 0

    assert re.search(f"{crab.name}\\s*Submitted: 0, Running: 10, Transferring: 5, Finished: 10, Failed: 5", result.stdout)

def test_status_when_failed_prints_message(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="finished")
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"])

    assert result.exit_code == 0
    assert re.search(f"{crab.name}\\s*Finished", result.stdout)

def test_status_saves_raw_crab_output_in_log_file(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    status_output = get_status_output(running=10, transferring=5, finished=10, failed=5)
    fp.register(["crab", "status", "-d", fp.any()], stdout=status_output)

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"])
    assert result.exit_code == 0

    with open(crab.get_log_file()) as f:
        assert status_output in f.read()

def test_status_when_all_jobs_are_finished_sets_status_to_finished(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(finished=50))

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"])
    assert result.exit_code == 0

    new_pot = load_pot("mypot")
    assert new_pot.get_crab(crab.name).status == "finished"

def test_status_when_unexpected_error_logs_error_in_log_file(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    def stub_raise(process):
        raise FileNotFoundError("some error message")

    fp.register(["crab", "status", "-d", fp.any()], callback=stub_raise)

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"])
    assert result.exit_code == 0

    with open(crab.get_log_file()) as f:
        "some error message" == f.read()

def test_status_with_no_cmsenv_exits_as_failure(set_valid_cmsenv):
    set_valid_cmsenv(False)

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "cmsenv" in result.stdout.lower()

def test_status_with_no_grid_cert_exists_as_failure(set_valid_grid_cert):
    set_valid_grid_cert(False)

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "grid certificate" in result.stdout.lower()

