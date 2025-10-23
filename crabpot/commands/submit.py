import click
from crabpot import util
from crabpot import runner
from crabpot.exceptions import MissingPotError, MissingCrabError
import datetime
import json
import subprocess

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

    try:
        pot, crabs = util.get_crabs_from_target(target, status="unsubmitted")
    except MissingPotError as e:
        raise click.ClickException(str(e))
    except MissingCrabError as e:
        raise click.ClickException(str(e))

    if len(crabs) == 0:
        raise click.ClickException("No crab jobs to submit.")

    for crab in crabs:
        result = subprocess.run(["crab", "submit", crab.get_crab_config()], capture_output=True, text=True)

        if "Success: Your task has been delivered" in result.stdout:
            crab.status = "submitted"
            pot.save()
