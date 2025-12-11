import click
import crabpot.core as core
from crabpot.core.exceptions import EmptyNameError, InvalidNameError, ExistingNameError

@click.command
@click.argument("name")
def create_pot(name):
    try:
        core.create_pot(name)
        click.echo(f"Successfully created pot \"{name}\"")
    except EmptyNameError:
        raise click.BadParameter("cannot be blank", param_hint="name")
    except InvalidNameError:
        raise click.BadParameter("can only be alphanumeric characters and underscores", param_hint="name")
    except ExistingNameError:
        raise click.BadParameter(f"pot with name \"{name}\" already exists", param_hint="name")
