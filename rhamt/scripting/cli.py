import click

from rhamt.scripting.shell import main as shell


@click.group()
def cli():
    """CLI Tool for RHAMT"""
    pass


cli.add_command(shell, name="shell")

if __name__ == "__main__":
    cli()
