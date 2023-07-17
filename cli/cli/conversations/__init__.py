from pathlib import Path
from typing import List

import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Conversation commands")


@app.command(rich_help_panel="Conversation commands")
def get(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of your conversation.")],
):
    """
    It returns all the messages of one conversation.
    """
    print(ctx.parent.obj["r"].get(f"broker/conversations/{id}"))


@app.command(rich_help_panel="Conversation commands", name="list")
def _list(
    ctx: typer.Context,
    sender_id: Annotated[
        str,
        typer.Argument(help="The id of the sender to get all the conversations from."),
    ],
):
    """
    It returns a list of all the conversations belonging to one user.
    """
    print(ctx.parent.obj["r"].get(f"broker/conversations?sender={sender_id}"))


@app.command(rich_help_panel="Conversation commands")
def download(
    ctx: typer.Context,
    ids: Annotated[
        List[str], typer.Argument(help="A list of the ids of your conversations.")
    ],
    download_path: Annotated[
        str, typer.Option(help="The path where you want to download the file.")
    ] = None,
):
    """
    It will download a text file if you provide only one id or a zip file if more than one of all the conversations contents.
    """
    print("Downloading...")
    r = ctx.parent.obj["r"].post(
        f"broker/conversations/{','.join(ids)}/download/", json=False
    )
    filename = r.headers["content-disposition"].split("attachment; filename=")[1]
    if not download_path:
        download_path = str(Path.home() / "Downloads" / filename)
    open(download_path, "wb").write(r.content)
    print(f"Downloaded into {download_path}")


if __name__ == "__main__":
    app()
