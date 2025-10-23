import pytest
from click.testing import CliRunner
from crabpot.cli import main
from crabpot.pot import Pot
from crabpot.util import load_pot
from tests.factories import create_pot, create_crab
import re

RESUBMIT_SUCCESS_RESPONSE = [
    "Resubmitted task on the CRAB server.",
    "Task name: 251003_194836:username_crab_TestRequest",
    "Log file is /some/path/to/log/file/crab.log",
]

RESUBMIT_FAILURE_RESPONSE = [
    "No failed jobs to resubmit"
]

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
        percentage = val / total if total > 0 else 0
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
    def test_resubmit_calls_crab_resubmit_on_all_crabs_with_failed_jobs(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab1 = create_crab(pot, status="submitted")
        crab2 = create_crab(pot, status="submitted")
        crab3 = create_crab(pot, status="unsubmitted")
        pot.save()

        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=5, failed=3))
        fp.register(["crab", "resubmit", "-d", fp.any()], stdout=RESUBMIT_SUCCESS_RESPONSE)
        fp.keep_last_process(True)

        runner = CliRunner()
        result = runner.invoke(main, args=["resubmit", "mypot"])
        assert result.exit_code == 0

        assert fp.call_count(["crab", "resubmit", "-d", fp.any()]) == 2
        assert ["crab", "resubmit", "-d", crab1.get_crab_request_dir()] in fp.calls
        assert ["crab", "resubmit", "-d", crab2.get_crab_request_dir()] in fp.calls

    def test_resubmit_with_incorrect_pot_name_exits_as_failure(self):
        runner = CliRunner()
        result = runner.invoke(main, args=["resubmit", "somepot"])

        assert result.exit_code != 0
        assert "pot somepot not found" in result.stdout.lower()

    def test_resubmit_with_unexpected_error_continues_on_later_crabs(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab1 = create_crab(pot, status="submitted")
        crab2 = create_crab(pot, status="submitted")
        pot.save()

        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=10, failed=5))
        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=10, failed=5))

        def stub_raise(process):
            raise Exception("Some error")

        fp.register(["crab", "resubmit", "-d", fp.any()], callback=stub_raise)
        fp.register(["crab", "resubmit", "-d", fp.any()], stdout=RESUBMIT_SUCCESS_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(main, args=["resubmit", "mypot"])
        assert result.exit_code == 0

        assert fp.call_count(["crab", "resubmit", "-d", fp.any()]) == 2
        assert ["crab", "resubmit", "-d", crab2.get_crab_request_dir()] in fp.calls

class TestWithCrabTarget:
    def test_resubmit_with_failed_jobs_calls_crab_resubmit(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        crab_other = create_crab(pot, status="submitted")
        pot.save()

        fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=5, failed=3))
        fp.register(["crab", "resubmit", "-d", fp.any()], stdout=RESUBMIT_SUCCESS_RESPONSE)

        runner = CliRunner()
        result = runner.invoke(main, args=["resubmit", f"mypot.{crab.name}"])
        assert result.exit_code == 0

        assert fp.call_count(["crab", "resubmit", "-d", fp.any()]) == 1
        assert ["crab", "resubmit", "-d", crab.get_crab_request_dir()] in fp.calls

    def test_resubmit_with_incorrect_pot_name_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["resubmit", f"otherpot.{crab.name}"])

        assert result.exit_code != 0
        assert f"pot otherpot not found" in result.stdout.lower()

    def test_resubmit_with_incorrect_crab_name_exits_as_failure(self, create_pot, create_crab, fp):
        pot = create_pot(name="mypot")
        crab = create_crab(pot, status="submitted")
        pot.save()

        runner = CliRunner()
        result = runner.invoke(main, args=["resubmit", "mypot.othercrab"])

        assert result.exit_code != 0
        assert f"crab othercrab not found" in result.stdout.lower()

def test_resubmit_saves_crab_output_to_log(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    status_output = get_status_output(running=5, failed=3)
    resubmit_output = "\n".join(RESUBMIT_SUCCESS_RESPONSE)

    fp.register(["crab", "status", "-d", fp.any()], stdout=status_output)
    fp.register(["crab", "resubmit", "-d", fp.any()], stdout=resubmit_output)

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "mypot"])
    assert result.exit_code == 0

    with open(crab.get_log_file()) as f:
        log_contents = f.read()
        assert resubmit_output in log_contents

def test_resubmit_with_unexpected_error_saves_error_to_log(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    def stub_raise(process):
        raise FileNotFoundError("test error message")

    fp.register(["crab", "status", "-d", fp.any()], callback=stub_raise)

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "mypot"])
    assert result.exit_code == 0

    with open(crab.get_log_file()) as f:
        log_contents = f.read()
        assert "test error message" in log_contents

def test_resubmit_with_unexpected_error_prints_message(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    def stub_raise(process):
        raise Exception("test error")

    fp.register(["crab", "status", "-d", fp.any()], callback=stub_raise)

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "mypot"])
    assert result.exit_code == 0

    assert "Unexpected error" in result.stdout

def test_resubmit_with_no_failed_jobs_doesnt_call_crab_resubmit(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=10, finished=5))

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "mypot"])
    assert result.exit_code == 0

    assert fp.call_count(["crab", "resubmit", "-d", fp.any()]) == 0

def test_resubmit_when_status_wasnt_called_previously_calls_crab_status(create_pot, create_crab, fp):
    pot = create_pot(name="mypot")
    crab = create_crab(pot, status="submitted")
    pot.save()

    fp.register(["crab", "status", "-d", fp.any()], stdout=get_status_output(running=5, failed=3))
    fp.register(["crab", "resubmit", "-d", fp.any()], stdout=RESUBMIT_SUCCESS_RESPONSE)

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "mypot"])
    assert result.exit_code == 0

    assert fp.call_count(["crab", "status", "-d", fp.any()]) >= 1

def test_resubmit_with_no_cmsenv_exits_as_failure(set_valid_cmsenv):
    set_valid_cmsenv(False)

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "cmsenv" in result.stdout.lower()

def test_resubmit_with_no_grid_cert_exits_as_failure(set_valid_grid_cert):
    set_valid_grid_cert(False)

    runner = CliRunner()
    result = runner.invoke(main, args=["resubmit", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "grid certificate" in result.stdout.lower()
