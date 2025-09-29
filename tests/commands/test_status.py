from click.testing import CliRunner
from crabpot.cli import main
from crabpot.pot import Pot

STATUS_OUTPUT = """
Rucio client intialized for account myaccount
CRAB project directory:         /some/path/.crabpot/mypot/crab
Task name:                      250924_173012:my_crab_request
Grid scheduler - Task Worker:   crab3@vocms0121.cern.ch - crab-prod-tw01
Status on the CRAB server:      SUBMITTED
Task URL to use for HELP:       https://cmsweb.cern.ch/crabserver/ui/task/250924_173012%3Amy_crab_request
Dashboard monitoring URL:       https://monit-grafana.cern.ch/d/cmsTMDetail/cms-task-monitoring-task-view?orgId=11&var-user=myusername&var-task=250924_173012%3Amy_crab_request
Status on the scheduler:        COMPLETED

Jobs status:                    finished                20.0% (10/50)
                                running                 30.0%  (15/50)
                                submitted               10.0%  (5/50)
                                failed                  40.0%  (20/50)

Summary of run jobs:
 * Memory: 86MB min, 3083MB max, 1192MB ave
 * Runtime: 0:01:03 min, 0:15:59 max, 0:04:11 ave
 * CPU eff: 11% min, 80% max, 53% ave
 * Waste: 989:45:01 (81% of total)

Log file is /some/path/.crabpot/mypot/crab/crab.log
"""

def test_status_with_submitted_jobs_prints_message(cmd_runner):
    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.status = "submitted"
    pot.save()

    cmd_runner.set_stdout(STATUS_OUTPUT)

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 1
    cmd, kwards = cmd_runner.received_commands[0]
    assert cmd == ["crab", "status", "-d", ".crabpot/mypot/crab/crab_dir"]

    assert "running: 15" in result.stdout.lower()
    assert "finished: 10" in result.stdout.lower()
    assert "submitted: 5" in result.stdout.lower()
    assert "failed: 20" in result.stdout.lower()

def test_status_with_some_unsubmitted_crabs_skips_those(cmd_runner, tmp_path):
    path = tmp_path / "crab_config.py.jinja"
    path.write_text("some text")

    pot = Pot("mypot")
    crab_submitted = pot.create_crab("crab_submitted")
    crab_submitted.status = "submitted"
    crab_unsubmitted = pot.create_crab("crab_unsubmitted")
    crab_unsubmitted.add_template_file(str(path), is_crab_config=True)
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 1
    cmd, kwards = cmd_runner.received_commands[0]
    assert cmd == ["crab", "status", "-d", ".crabpot/mypot/crab_submitted/crab_dir"]

def test_status_with_no_submitted_crabs_prints_message(cmd_runner, tmp_path):
    path = tmp_path / "crab_config.py.jinja"
    path.write_text("some text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path), is_crab_config=True)
    pot.save()

    runner = CliRunner()
    result = runner.invoke(main, args=["status", "mypot"], catch_exceptions=False)

    assert len(cmd_runner.received_commands) == 0
    assert "no submitted crabs" in result.stdout.lower()

def test_status_when_pot_not_found_exits_as_failure():
    runner = CliRunner()
    result = runner.invoke(main, args=["status", "sample"], catch_exceptions=False)

    assert result.exit_code != 0
    assert "pot sample not found" in result.stdout.lower()

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

