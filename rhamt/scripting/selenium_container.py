import shutil
import click
from rhamt.utils import conf
import subprocess


class SeleniumContainer(object):
    def __init__(self, client=None, name=None, image=None, vnc_port=None, webdriver_port=None,
                 network=None):
        default_conf = conf.get_config("selenium")
        self.client = client or default_conf.client
        self.name = name or default_conf.name
        self.image = image or default_conf.image
        self.vnc_port = vnc_port or default_conf.vnc_port
        self.webdriver_port = webdriver_port or default_conf.webdriver_port
        self.network = network or default_conf.network

        assert shutil.which(self.client)

    @property
    def is_running(self):
        cmd = subprocess.run(["docker", "ps"], stdout=subprocess.PIPE)
        return self.name in cmd.stdout.decode()

    def start(self):
        if not self.is_running:
            cmd = [
                    self.client,
                    "run",
                    "-d",
                    "--rm",
                    "--expose",
                    "5999",
                    "--expose",
                    "4444",
                    "-p",
                    f"{self.vnc_port}:5999",
                    "-p",
                    f"{self.webdriver_port}:4444",
                    "--network",
                    self.network,
                    "--name",
                    self.name,
                    self.image,
                ]
            subprocess.run(cmd)
        else:
            click.echo(f"{self.name} container already in running state")

    def stop(self):
        if self.is_running:
            subprocess.run([self.client, "stop", self.name])
        else:
            click.echo(f"{self.name} container not in running state")


@click.group()
def main():
    """Selenium container for testing"""
    pass


@main.command(help="Starts selenium container")
@click.option("-w", "--watch", is_flag=True, help="After start open VNC viewer")
@click.pass_context
def start(ctx, watch):
    sel = SeleniumContainer()
    sel.start()

    if watch:
        ctx.invoke(viewer)


@main.command(help="Stop selenium container")
def stop():
    sel = SeleniumContainer()
    sel.stop()


@main.command(help="Current Status of container")
def status():
    sel = SeleniumContainer()
    click.echo("Running" if sel.is_running else "Stopped")


@main.command(help="Command executor of selenium container")
def executor():
    sel = SeleniumContainer()
    return f"http://localhost:{sel.webdriver_port}/wd/hub"


@main.command(help="VNC url for selenium container")
def vnc():
    sel = SeleniumContainer()
    return f"localhost:{sel.vnc_port}"


@main.command(help="Open VNC viewer for selenium container")
def viewer():
    viewer = conf.get_config("selenium").vncviewer
    sel = SeleniumContainer()

    if not viewer:
        click.echo("No VNC viewer found in config file")
        exit(1)

    if not sel.is_running:
        click.echo(f"{sel.name} not in running state")
        exit(1)

    assert shutil.which(viewer)
    subprocess.run([viewer, f"localhost:{sel.vnc_port}"])
