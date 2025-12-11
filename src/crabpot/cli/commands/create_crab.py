import click
import crabpot.core as core
from crabpot.core.exceptions import EmptyNameError, InvalidNameError, ExistingNameError, MissingPotError

@click.command
@click.argument("pot_name")
@click.argument("crab_name")
def create_crab(pot_name, crab_name):
    try:
        core.create_crab(pot_name, crab_name)
        click.echo(f"Successfully created crab \"{crab_name}\" in pot \"{pot_name}\"")
    except EmptyNameError:
        raise click.BadParameter("cannot be blank", param_hint="crab_name")
    except InvalidNameError:
        raise click.BadParameter("can only be alphanumeric characters and underscores", param_hint="crab_name")
    except ExistingNameError:
        raise click.BadParameter(f"crab with name \"{crab_name}\" already exists in pot \"{pot_name}\"", param_hint="crab_name")
    except MissingPotError:
        raise click.BadParameter(f"cannot find pot \"{pot_name}\"")
