import click
from crabpot import util
from crabpot import runner
import datetime
import json
from multiprocessing import Process

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
        crabs = [pot.get_crab(crab_name)]
        if crabs[0].status != "unsubmitted":
            click.echo("No crab jobs to submit.")
            return
    else:
        crabs = pot.get_crabs(status="unsubmitted")
        if len(crabs) == 0:
            click.echo("No crab jobs to submit.")
            return

    for crab in crabs:
        def submit():
            runner.runner.cmd("submit", config=crab.get_crab_config())

        p = Process(target=submit)
        p.start()
        p.join()

        crab.status = "submitted"

        # Save here so that if there is an error, we still are good with previously done things
        # Can we test it with pretending there is an exception?
        # If we do fail though, don't set status to submitted

        pot.save()
