import click
import subprocess
from crabpot import util
from crabpot.exceptions import MissingPotError, MissingCrabError
import re
import tabulate

PATTERN = r"\b(transferring|finished|running|submitted|failed)\b\s+\d+\.\d+%\s*\(\s*(\d+)\/\d+\)"

def get_submitted_status(pot, crab):
    """Get status counts for a submitted crab if not already cached."""
    if crab.status_counts:
        # Already have status counts cached
        return crab.status_counts

    try:
        result = subprocess.run(["crab", "status", "-d", crab.get_crab_request_dir()], capture_output=True, text=True)
        with open(crab.get_log_file(), "a") as f:
            f.write(result.stdout)

        matches = re.findall(PATTERN, result.stdout)

        job_statuses = {m[0]: int(m[1]) for m in matches}
        labels = ["submitted", "running", "transferring", "finished", "failed"]
        crab.status_counts = {label: job_statuses.get(label, 0) for label in labels}
        pot.save()

        return crab.status_counts
    except Exception as e:
        with open(crab.get_log_file(), "a") as f:
            f.write(f"Received unexpected exception while running crab status\n")
            f.write(f"{e}\n")
        return None

def resubmit_crab(pot, crab):
    """Attempt to resubmit a crab if it has failed jobs."""
    return_str = ""

    try:
        # Get status if not cached
        status_counts = get_submitted_status(pot, crab)

        if status_counts is None:
            return_str += f"Unexpected error while processing crab {crab.name}\n"
            return return_str

        failed_jobs = status_counts.get("failed", 0)

        if failed_jobs == 0:
            return_str += f"No failed jobs to resubmit for {crab.name}\n"
            return return_str

        # Call crab resubmit
        result = subprocess.run(["crab", "resubmit", "-d", crab.get_crab_request_dir()], capture_output=True, text=True)

        with open(crab.get_log_file(), "a") as f:
            f.write(result.stdout)

        return_str += f"Resubmitted {failed_jobs} failed jobs\n"

    except Exception as e:
        return_str += f"Unexpected error while processing crab {crab.name}\n"

        with open(crab.get_log_file(), "a") as f:
            f.write(f"Received unexpected exception while running crab resubmit\n")
            f.write(f"{e}\n")

    return return_str

@click.command()
@click.argument("target")
def resubmit(target):
    """Resubmit failed CRAB jobs from a pot or a specific crab.

    \b
    TARGET can be one of:
        - POT_NAME               Resubmits all crabs in the pot with failed jobs
        - POT_NAME.CRAB_NAME     Resubmit a single crab in the pot
    """

    if not util.cert.check_cmsenv():
        raise click.ClickException("No CMS environment found. Please run cmsenv.")

    if not util.cert.check_grid_cert():
        raise click.ClickException("No valid grid certificate found. Please run voms proxy-init.")

    try:
        pot, crabs = util.get_crabs_from_target(target, status="submitted")
    except MissingPotError as e:
        raise click.ClickException(str(e))
    except MissingCrabError as e:
        raise click.ClickException(str(e))

    name_strs = [crab.name for crab in crabs]
    results_strs = []
    with click.progressbar(crabs, label=f"Resubmitting failed jobs for {len(crabs)} crabs.") as bar:
        for crab in bar:
            results_strs.append(resubmit_crab(pot, crab))

    click.echo(tabulate.tabulate(zip(name_strs, results_strs), tablefmt="plain"))
