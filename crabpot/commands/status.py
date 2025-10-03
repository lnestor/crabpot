import click
import subprocess
from crabpot import util
import re

PATTERN = r"\b(transferring|finished|running|submitted|failed)\b\s+\d+\.\d+%\s*\(\s*(\d+)\/\d+\)"

def split_target(target):
    if "." in target:
        split = target.split(".")
        return split[0], split[1]
    else:
        return target, None

@click.command
@click.argument("target")
def status(target):
    """Read the status of the CRAB jobs for a given pot."""

    if not util.cert.check_cmsenv():
        raise click.ClickException("No CMS environment found. Please run cmsenv.")

    if not util.cert.check_grid_cert():
        raise click.ClickException("No valid grid certificate found. Please run voms proxy-init.")

    pot_name, crab_name = split_target(target)
    pot = util.load_pot(pot_name)
    if pot is None:
        raise click.ClickException(f"Pot {pot_name} not found.")

    if crab_name is not None:
        crabs = [pot.get_crab(crab_name)]
        if crabs[0] is None:
            raise click.ClickException(f"Crab {crab_name} not found.")
    else:
        crabs = pot.get_crabs()
        if len(crabs) == 0:
            raise click.ClickException(f"No submitted crabs in pot {pot_name}.")

    result_str = ""
    with click.progressbar(crabs, label=f"Reading status for {len(crabs)} crabs.") as bar:
        for crab in bar:
            if crab.status == "unsubmitted":
                result_str += f"{crab.name} - Unsubmitted"
            elif crab.status == "finished":
                result_str += f"{crab.name} - Finished"
            elif crab.status == "submitted":
                try:
                    result = subprocess.run(["crab", "status", "-d", crab.get_crab_request_dir()], capture_output=True, text=True)
                    with open(crab.get_log_file(), "a") as f:
                        f.write(result.stdout)

                    matches = re.findall(PATTERN, result.stdout)

                    job_statuses = {m[0]: m[1] for m in matches}
                    labels = ["submitted", "running", "transferring", "finished", "failed"]
                    job_str = ", ".join(f"{label.title()}: {job_statuses.get(label, 0)}" for label in labels)
                    result_str += f"{crab.name} - {job_str}\n"

                    non_finished_jobs = sum(int(count) for status, count in job_statuses.items() if status != "finished")
                    finished_jobs = int(job_statuses.get("finished", 0))

                    if non_finished_jobs == 0 and finished_jobs > 0:
                        crab.status = "finished"
                        pot.save()
                except Exception as e:
                    result_str += f"Unexpected error while processing crab {crab.name}\n"

                    with open(crab.get_log_file(), "a") as f:
                        f.write(f"Received unexpected exception while running crab status\n")
                        f.write(f"{e}\n")

    click.echo(result_str)

