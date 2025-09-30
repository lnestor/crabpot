import click
from crabpot import runner
from crabpot import util
import re

PATTERN = r"\b(finished|running|submitted|failed)\b\s+\d+\.\d+%\s*\((\d+)\/\d+\)"

@click.command
@click.argument("pot_name")
def status(pot_name):
    """Read the status of the CRAB jobs for a given pot."""

    if not util.cert.check_cmsenv():
        raise click.ClickException("No CMS environment found. Please run cmsenv.")

    if not util.cert.check_grid_cert():
        raise click.ClickException("No valid grid certificate found. Please run voms proxy-init.")

    pot = util.load_pot(pot_name)
    if pot is None:
        raise click.ClickException(f"Pot {pot_name} not found.")

    crabs = pot.get_crabs(status="submitted")
    if len(crabs) == 0:
        click.echo(f"No submitted crabs in pot {pot_name}.")
        return

    for crab in crabs:
        result = runner.runner.cmd("status", dir=crab.get_crab_dir())
        matches = re.findall(PATTERN, result.stdout)

        click.echo(crab.name)
        for match in matches:
            click.echo(f"{match[0]}: {match[1]}")
