import json
from io import UnsupportedOperation

import typer
from rich import print
from typing_extensions import Annotated

from chatfaq_cli.helpers import CONFIG_FILE_PATH, set_config

app = typer.Typer(help="Configuration commands")


@app.command(rich_help_panel="Configuration commands", name="auth")
def auth(ctx: typer.Context, token: Annotated[str, typer.Argument(help="The token.")]):
    """
    It stores your ChatFAQ auth token for later authentication.
    """
    set_config("token", token)
    print("Token saved")


@app.command(rich_help_panel="Configuration commands", name="host")
def host(
    ctx: typer.Context,
    host_name: Annotated[
        str, typer.Argument(help="The host (e.g. http://localhost:8000).")
    ],
):
    """
    It stores your ChatFAQ host.
    """
    set_config("host", host_name)
    print("Host saved")


if __name__ == "__main__":
    app()
