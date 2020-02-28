import subprocess


def test_rhamt_command():
    result = subprocess.run("rhamt", stdout=subprocess.PIPE)
    assert result.returncode == 0
    assert "CLI Tool for RHAMT" in result.stdout.decode()
