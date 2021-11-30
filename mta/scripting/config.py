import click
from yaml import safe_dump
from yaml import safe_load

from mta.utils.path import CONF_PATH

ENV_LOCAL_CONF = CONF_PATH / "env.local.yaml"
ENV_CONF = CONF_PATH / "env.yaml"


@click.group()
def main():
    """MTA Configuration."""
    pass


@main.command(help="Create env.local.yaml file")
@click.option(
    "-h", "--hostname", default="http://localhost:8080", help="Hostname of the target application"
)
@click.option(
    "-ocph", "--ocphostname", default="http://mta-mta.apps.mta01.cnv-qe.rhcloud.com", help="OCP Hostname of the target application"
)
@click.option(
    "-ocpsh", "--ocpsecurehostname", default="https://secure-mta-mta.apps.mta01.cnv-qe.rhcloud.com", help="OCP Secure Hostname of the target application"
)
@click.option("-p", "--password", default="password", help="MTA password")
@click.option(
    "-d",
    "--webdriver",
    default="Remote",
    type=click.Choice(["Remote", "Chrome", "Firefox"]),
    help="Webdriver",
)
@click.option(
    "-w", "--wharf", default=None, help="Address of the wharf server for remote webdrivers"
)
@click.option(
    "-e", "--executor", default="http://localhost:4444/wd/hub", help="Selenium Command executor"
)
@click.option(
    "-b",
    "--browser",
    default="chrome",
    type=click.Choice(["chrome", "firefox"]),
    help="Browser name.",
)
@click.option("-fh", "--ftp-host", default=None, help="FTP server hostname")
@click.option("-fu", "--ftp-username", default=None, help="FTP server username")
@click.option("-fp", "--ftp-password", default=None, help="FTP server password")
@click.option("-o", "--output-file", default=ENV_LOCAL_CONF, help="Output file for yaml dump")
def local_env(
    hostname,
    ocphostname,
    ocpsecurehostname,
    password,
    webdriver,
    wharf,
    executor,
    browser,
    ftp_host,
    ftp_username,
    ftp_password,
    output_file,
):
    with open(ENV_CONF, "r") as env_conf:
        conf = safe_load(env_conf)

    conf["application"]["hostname"] = hostname
    conf["application"]["ocphostname"] = ocphostname
    conf["application"]["ocpsecurehostname"] = ocpsecurehostname
    conf["application"]["password"] = password
    conf["browser"]["webdriver"] = webdriver
    conf["browser"]["webdriver_options"]["command_executor"] = executor
    conf["browser"]["webdriver_options"]["desired_capabilities"]["browserName"] = browser
    conf["ftpserver"]["host"] = ftp_host
    conf["ftpserver"]["credentials"]["username"] = ftp_username
    conf["ftpserver"]["credentials"]["password"] = ftp_password

    if wharf:
        conf["browser"]["webdriver_wharf"] = wharf

    with open(output_file, "w") as env_conf:
        return safe_dump(conf, env_conf, default_flow_style=False)
