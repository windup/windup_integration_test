import click

from rhamt.scripting.selenium_container import main as sel_container
from rhamt.scripting.shell import main as shell


@click.group()
def cli():
    """CLI Tool for RHAMT"""
    pass


cli.add_command(shell, name="shell")
cli.add_command(sel_container, name="selenium")

if __name__ == "__main__":
    cli()
