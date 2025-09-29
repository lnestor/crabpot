import click
import importlib.util
from crabpot.pot import Pot
from crabpot.exceptions import MissingTemplateError
import traceback

def load_pot(filename):
    spec = importlib.util.spec_from_file_location("user_config", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.pot

@click.command()
@click.argument(
    "config",
    type=click.Path(exists=True),
)
def create(config):
    try:
        pot = load_pot(config)
    except SyntaxError as e:
        msg = traceback.format_exc()
        raise click.ClickException(f"Config file has a syntax error.\n{msg}")

    if pot.name == "":
        raise click.ClickException("Invalid config file.")

    if pot.exists_on_disk():
        raise click.ClickException("Pot with name {config.name} already exists.")

    try:
        pot.save()
    except MissingTemplateError as e:
        raise click.ClickException(f"Missing template files.\n{e}")
