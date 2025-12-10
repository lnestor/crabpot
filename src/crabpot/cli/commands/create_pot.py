import click
import crabpot.core.commands as core
from crabpot.core.exceptions import EmptyPotNameError, InvalidPotNameError, ExistingPotNameError

@click.command
@click.argument("name")
def create_pot(name):
    try:
        core.create_pot(name)
        click.echo(f"Successfully created pot \"{name}\"")
    except EmptyPotNameError:
        raise click.BadParameter("cannot be blank", param_hint="name")
    except InvalidPotNameError:
        raise click.BadParameter("can only be alphanumeric characters and underscores", param_hint="name")
    except ExistingPotNameError:
        raise click.BadParameter(f"pot with name \"{name}\" already exists", param_hint="name")
