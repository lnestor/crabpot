import click
import crabpot.core as core

@click.command
def list_pots():
    pots = core.get_pots()

    if len(pots) > 0:
        click.echo("\n".join(pots))
    else:
        click.echo("No pots found")
