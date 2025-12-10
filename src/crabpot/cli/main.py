import click
from crabpot.cli.commands import create_pot, list_pots
from crabpot.tui.app import CrabpotApp

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        app = CrabpotApp()
        app.run()

main.add_command(create_pot.create_pot)
main.add_command(list_pots.list_pots)
