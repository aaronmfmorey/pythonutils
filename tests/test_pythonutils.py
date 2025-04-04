from typer.testing import CliRunner
import os
from dotenv import dotenv_values
from pythonutils import __app_name__, __version__, cli

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

def test_dot_env_to_keys_file():
    result = runner.invoke(cli.app, ["env-key-values -p ."])
    # assert(result.exit_code == 0)
    assert(os.path.exists(".env.sample"))
    assert(dotenv_values(".env").keys() == dotenv_values(".env.sample").keys())

def test_goodreads_csv_to_json():
    result = runner.invoke(cli.app, ["goodreads-csv"])
    assert(result.exit_code == 0)
    # TODO AMM - add more tests here