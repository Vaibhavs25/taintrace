from click.testing import CliRunner

from taintrace import __version__
from taintrace.cli import cli


def test_version_long_flag():
    result = CliRunner().invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert result.output == f"cli, version {__version__}\n"


def test_version_short_flag():
    result = CliRunner().invoke(cli, ["-v"])

    assert result.exit_code == 0
    assert result.output == f"cli, version {__version__}\n"
