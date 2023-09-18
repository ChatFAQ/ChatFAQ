from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Generation Config commands")


@app.command(rich_help_panel="Generation Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Generation Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/generation-configs/"))


@app.command(rich_help_panel="Generation Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Generation Config you want to delete.")],
):
    """
    Delete an existing Generation Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/generation-configs/{id}")
    print(res)
