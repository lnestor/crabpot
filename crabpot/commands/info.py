import click
from crabpot import util

@click.command()
@click.argument("target")
@click.option("--v", "verbose", is_flag=True)
def info(target, verbose):
    pot = util.load_pot(target)
    if pot is None:
        raise click.ClickException(f"Pot {target} not found.")

    fmt = click.HelpFormatter()
    fmt.write_text(f"Info for pot {target}")
    fmt.indent()
    fmt.write_text(f"Number of crabs: {len(pot.get_crabs())}")
    fmt.indent()
    fmt.write_text(f"Unsubmitted: {len(pot.get_crabs(status='unsubmitted'))}")
    fmt.write_text(f"Submitted: {len(pot.get_crabs(status='submitted'))}")
    fmt.dedent()
    fmt.dedent()

    if verbose:
        fmt.write_text("")
        for crab in pot.get_crabs():
            fmt.write_text(crab.name)
            fmt.indent()
            fmt.write_text(f"Status: {crab.status}")
            fmt.dedent()

        click.echo_via_pager(fmt.getvalue())
    else:
        click.echo(fmt.getvalue())
