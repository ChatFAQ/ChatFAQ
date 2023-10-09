from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Retriever Config commands")


@app.command(rich_help_panel="Retriever Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Retriever Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/retriever-configs/"))


@app.command(rich_help_panel="Retriever Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Retriever Config you want to delete.")],
):
    """
    Delete an existing Retriever Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/retriever-configs/{id}")
    print(res)
