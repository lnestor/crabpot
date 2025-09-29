import click
from crabpot import util
from crabpot import runner
import datetime
import json

@click.command()
@click.argument("pot_name")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Test generation of config files without actually submitting to CRAB."
)
def submit(pot_name, dry_run):
    """Submit CRAB jobs for a given pot."""

    if not util.cert.check_cmsenv():
        raise click.ClickException("No CMS environment found. Please run cmsenv.")

    if not util.cert.check_grid_cert():
        raise click.ClickException("No valid grid certificate found. Please run voms proxy-init.")

    pot = util.load_pot(pot_name)
    if pot is None:
        raise click.ClickException(f"Pot {pot_name} not found.")

    crabs = pot.get_crabs(status="unsubmitted")
    if len(crabs) == 0:
        click.echo("No crab jobs to submit.")
        return

    for crab in crabs:
        crab.generate()

        if not dry_run:
            runner.runner.run(["crab", "submit", "-c", crab.get_crab_config()])
