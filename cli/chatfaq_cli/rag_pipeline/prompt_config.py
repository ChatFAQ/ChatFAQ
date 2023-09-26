from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Prompt Config commands")


@app.command(rich_help_panel="Prompt Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Prompt Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/prompt-configs/"))


@app.command(rich_help_panel="Prompt Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Prompt Config you want to delete.")],
):
    """
    Delete an existing Prompt Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/prompt-configs/{id}")
    print(res)
