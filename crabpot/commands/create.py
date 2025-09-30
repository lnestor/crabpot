import click
import importlib.util
from crabpot.pot import Pot
import traceback
from pathlib import Path

def load_pot(filename):
    spec = importlib.util.spec_from_file_location("user_config", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.pot

def get_miss_templates(pot):
    missing_templates = {}
    for crab in pot.get_crabs(status="unsubmitted"):
        missing_templates[crab.name] = []
        for (template, _) in crab.templates:
            if not Path(template).exists():
                missing_templates[crab.name].append(template)

        if len(missing_templates[crab.name]) == 0:
            del missing_templates[crab.name]

    return missing_templates

def fmt_miss_template_msg(missing_templates):
    template_str = "\n".join(f"{name}: {', '.join(templates)}" for name, templates in missing_templates.items())
    return f"Missing template files:\n\n{template_str}"

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
        raise click.ClickException(f"Pot with name {pot.name} already exists.")

    missing_templates = get_miss_templates(pot)
    if len(missing_templates) > 0:
        raise click.ClickException(fmt_miss_template_msg(missing_templates))

    for crab in pot.get_crabs(status="unsubmitted"):
        crab.generate()

    pot.save()
