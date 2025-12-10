import click
import crabpot.core.commands as core

@click.command
def list_pots():
    pots = core.get_pots()

    if len(pots) > 0:
        click.echo("\n".join(pot.name for pot in pots))
    else:
        click.echo("No pots found")
