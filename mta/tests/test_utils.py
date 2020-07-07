import subprocess

import pytest


@pytest.mark.ci
def test_mta_command():
    result = subprocess.run("mta", stdout=subprocess.PIPE)
    assert result.returncode == 0
    assert "CLI Tool for MTA" in result.stdout.decode()
