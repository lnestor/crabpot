import click
from crabpot import util
import shutil

@click.command()
@click.argument("target")
def reset(target):
    pot_name, crab_name = target.split(".")

    pot = util.load_pot(pot_name)
    if pot is None:
        raise click.ClickException(f"Pot {pot_name} not found.")

    crab = pot.get_crab(crab_name)
    if crab is None:
        raise click.ClickException(f"Crab {crab_name} not found.")

    crab.status = "unsubmitted"
    shutil.rmtree(crab.get_base_crab_dir())
    pot.save()
