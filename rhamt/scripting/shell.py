# -*- coding: utf-8 -*-
import os

import click
from IPython.terminal.interactiveshell import TerminalInteractiveShell

IMPORTS = [
    "from rhamt.base.application import Application",
    "from rhamt.base.application.implementations.web_ui import navigate_to",
]


@click.command(help="Open an IPython shell")
@click.pass_obj
def main(obj):
    click.echo("Welcome to IPython designed for running RHAMT code.")
    ipython = TerminalInteractiveShell.instance()

    for code_import in IMPORTS:
        click.echo(f"> {code_import}")
        ipython.run_cell(code_import)

    # create default app
    ipython.run_cell("app = Application()")
    click.echo("> app = $magic Application")

    from rhamt.utils.path import CONF_PATH

    custom_import_path = os.path.join(CONF_PATH, "rhmt_shell_startup.py")

    if os.path.isfile(custom_import_path):
        with open(custom_import_path, "r") as custom_import_file:
            custom_import_code = custom_import_file.read()
        click.echo(f"Importing custom code:\n{custom_import_code.strip()}")
        ipython.run_cell(custom_import_code)
    else:
        click.echo(
            "You can create your own python file with imports you use frequently. "
            "Just create a conf/rhmt_shell_startup.py file in your repo. "
            "This file can contain arbitrary python code that is executed in this context."
        )
    ipython.interact()


if __name__ == "__main__":
    main()
