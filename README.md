<h1 align="center"> Windup - Integration tests </h1>

## Getting started:
#### Install the framework in developer mode:
1. Fork the repository
2. Follow the following steps (Minimum Python-3.6 required)

```shell
git clone https://github.com/<user>/windup_integration_tests.git
cd windup_integration_test
python3.8 -m venv .mta_venv
source .mta_venv/bin/activate
pip install -e .
```

**Note:** After this you should able to access `mta` command. `mta` is a command-line tool;
which help for test development. Check help (`mta --help`) for more information.

#### Configure your Environment:
The framework needs some configuration before actual use. Configuration file located at `mta/conf` directory.
**env.yaml** file holds your testing environment.
You need to change this as per your application `hostname` (web-console) and webdriver options.
The best practice is to create a local file with the name **env.local.yaml** and overwrite tags.


**Example:** Content of `env.local.yaml`; where we are overwriting `env.yaml` application hostname and
remote webdriver default options.

```yaml
application:
  hostname: http://foo.com

browser:
  webdriver: Remote
  webdriver_options:
    command_executor: http://localhost:4444/wd/hub
    desired_capabilities:
      acceptInsecureCerts: true
      acceptSslCerts: true
      browserName: firefox
      unexpectedAlertBehaviour: ignore
```

## mta:
Command line tool for windup integration tests development. You can find help with command
```shell
mta --help
```

`mta` providing fallowing features

#### Ipython Shell
```shell
mta shell --help
```
It is Ipython interactive shell for windup integration test development.
It will provide default imports like `navigate_to`, and `Application` object (app).
You can create your own python file with imports you use frequently.
Just create a `conf/mta_shell_startup.py` file in your repo.
This file can contain arbitrary python code that is executed in this context.

#### Selenium Container
```shell
mta selenium --help
```
It is containerized `webdriver`. It also includes a `VNC server` so that you can connect
and see what the browser is doing. This is also useful if you need to put a breakpoint in the test
and do some browser interaction.

The container client like `Docker` or `Podaman` should up and running on your system.
**selenium.yaml** file holds default selenium container config.
You can overwrite default by creating new file **selenium.local.yaml**.
