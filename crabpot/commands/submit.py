import click
from crabpot import util
from crabpot import runner
import datetime
import json

@click.command()
@click.argument("pot_name")
def submit(pot_name):
    """Submit CRAB jobs for a given pot."""

    if not util.cert.check_cmsenv():
        raise click.ClickException("No CMS environment found. Please run cmsenv.")

    if not util.cert.check_grid_cert():
        raise click.ClickException("No valid grid certificate found. Please run voms proxy-init.")

    pot = util.load_pot(pot_name)
    if pot is None:
        raise click.ClickException(f"Pot {pot_name} not found.")

    crabs = pot.get_unsubmitted_crabs()
    if len(crabs) == 0:
        click.echo("No crab jobs to submit.")
        return

    for crab in crabs:
        crab.generate()
        runner.runner.run(["crab", "submit", "-c", crab.get_crab_config()])
