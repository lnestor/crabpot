import click
import subprocess
from crabpot import util
import re
import tabulate

PATTERN = r"\b(transferring|finished|running|submitted|failed)\b\s+\d+\.\d+%\s*\(\s*(\d+)\/\d+\)"

def split_target(target):
    if "." in target:
        split = target.split(".")
        return split[0], split[1]
    else:
        return target, None

def get_submitted_status(pot, crab):
    return_str = ""

    try:
        result = subprocess.run(["crab", "status", "-d", crab.get_crab_request_dir()], capture_output=True, text=True)
        with open(crab.get_log_file(), "a") as f:
            f.write(result.stdout)

        matches = re.findall(PATTERN, result.stdout)

        job_statuses = {m[0]: int(m[1]) for m in matches}
        labels = ["submitted", "running", "transferring", "finished", "failed"]
        crab.status_counts = {label: job_statuses.get(label, 0) for label in labels}
        pot.save()

        job_str = ", ".join(f"{label.title()}: {crab.status_counts.get(label, 0)}" for label in labels)
        return_str += f"{job_str}\n"

        non_finished_jobs = sum(int(count) for status, count in job_statuses.items() if status != "finished")
        finished_jobs = int(job_statuses.get("finished", 0))

        if non_finished_jobs == 0 and finished_jobs > 0:
            crab.status = "finished"
            pot.save()
    except Exception as e:
        return_str += f"Unexpected error while processing crab {crab.name}\n"

        with open(crab.get_log_file(), "a") as f:
            f.write(f"Received unexpected exception while running crab status\n")
            f.write(f"{e}\n")

    return return_str

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

    name_strs = [crab.name for crab in crabs]
    results_strs = []
    with click.progressbar(crabs, label=f"Reading status for {len(crabs)} crabs.") as bar:
        for crab in bar:
            if crab.status == "unsubmitted":
                results_strs.append(f"Unsubmitted\n")
            elif crab.status == "finished":
                results_strs.append(f"Finished\n")
            elif crab.status == "submitted":
                if crab.status_counts:
                    finished = crab.status_counts.get("finished", 0)
                    failed = crab.status_counts.get("failed", 0)
                    submitted = crab.status_counts.get("submitted", 0)
                    running = crab.status_counts.get("running", 0)
                    transferring = crab.status_counts.get("transferring", 0)

                    if submitted == 0 and running == 0 and transferring == 0 and (finished > 0 or failed > 0):
                        labels = ["submitted", "running", "transferring", "finished", "failed"]
                        job_str = ", ".join(f"{label.title()}: {crab.status_counts.get(label, 0)}" for label in labels)
                        results_strs.append(f"{job_str}\n")
                    else:
                        results_strs.append(get_submitted_status(pot, crab))
                else:
                    results_strs.append(get_submitted_status(pot, crab))

    click.echo(tabulate.tabulate(zip(name_strs, results_strs), tablefmt="plain"))

