import click
from crabpot.commands import create, submit

@click.group()
def main():
    """crabpot - Easily handle CRAB operations on many datasets"""
    pass

main.add_command(create.create)
main.add_command(submit.submit)
