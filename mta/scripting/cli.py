import click

from mta.scripting.config import main as config
from mta.scripting.selenium_container import main as sel_container
from mta.scripting.shell import main as shell


@click.group()
def cli():
    """CLI Tool for MTA"""
    pass


cli.add_command(shell, name="shell")
cli.add_command(sel_container, name="selenium")
cli.add_command(config, name="conf")

if __name__ == "__main__":
    cli()
