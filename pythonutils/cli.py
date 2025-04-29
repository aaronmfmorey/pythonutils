from pathlib import Path
from typing import Optional
import typer
from . import __app_name__, __version__
from pythonutils.goodreads_csv_to_sqlite import GoodReadsCsvToSqlite
from pythonutils.dot_env_to_keys_file import DotEnvToKeysFile
from pythonutils import ERRORS, __app_name__, __version__, config

app = typer.Typer()

@app.command()
def goodreads_csv(
     download_files_response: str = typer.Option(
        str("Download Files?"),
        "--download-files",
        "-d",
    ),
) -> None:
    download_files = download_files_response == "1"
    typer.secho(f"Running Goodreads script!")
    goodreads = GoodReadsCsvToSqlite()
    goodreads.run(download_files)

@app.command()
def choose_command(
    command: str = typer.Option(
        str("Command"),
        "--command",
        "-c",
        prompt="""
What command do you want to run?
  1) GoodReads script
  2) Env File Script
""",
    ),
) -> None:
        match command:
            case "1":
                typer.secho(f"You selected command GoodReads", fg=typer.colors.GREEN)
                goodreads = GoodReadsCsvToSqlite()
                goodreads.run()
                return
            case "2":
                  typer.secho(f"I said there is no number 2!", fg=typer.colors.GREEN)
                  return
            case _:
                "Sorry!"
                return
             
@app.command()
def env_key_values(
     path: str = typer.Option(
        str("Path"),
        "--path",
        "-p"
     )
):
    DotEnvToKeysFile.create_file(path)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return