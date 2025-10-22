import click
from crabpot import util
from crabpot import runner
import datetime
import json
import subprocess

def split_target(target):
    if "." in target:
        split = target.split(".")
        return split[0], split[1]
    else:
        return target, None

@click.command()
@click.argument("target")
def submit(target):
    """
    Submit CRAB jobs from a pot or a specific crab.

    \b
    TARGET can be one of:
        - POT_NAME               Submits all crabs in the pot
        - POT_NAME.CRAB_NAME     Submit a single crab in the pot

    """

    if not util.cert.check_cmsenv():
        raise click.ClickException("No CMS environment found. Please run cmsenv.")

    if not util.cert.check_grid_cert():
        raise click.ClickException("No valid grid certificate found. Please run voms proxy-init.")

    pot_name, crab_name = split_target(target)
    pot = util.load_pot(pot_name)
    if pot is None:
        raise click.ClickException(f"Pot {pot_name} not found.")

    if crab_name is not None:
        if crab_name not in [c.name for c in pot.get_crabs()]:
            raise click.ClickException(f"Crab {crab_name} not found in pot {pot_name}")

        crabs = [pot.get_crab(crab_name)]
        if crabs[0].status != "unsubmitted":
            raise click.ClickException(f"Crab {crab_name} is already submitted")
    else:
        if len(pot.get_crabs()) == 0:
            raise click.ClickException(f"Pot {pot_name} is empty.")

        crabs = pot.get_crabs(status="unsubmitted")
        if len(crabs) == 0:
            raise click.ClickException("No crab jobs to submit.")

    for crab in crabs:
        result = subprocess.run(["crab", "submit", crab.get_crab_config()], capture_output=True, text=True)

        if "Success: Your task has been delivered" in result.stdout:
            crab.status = "submitted"
            pot.save()
