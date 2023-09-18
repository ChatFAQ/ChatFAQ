from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="RAG Config commands")


@app.command(rich_help_panel="RAG Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all RAG Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/rag-configs/"))


@app.command(rich_help_panel="RAG commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the RAG you want to delete.")],
):
    """
    Delete an existing RAG.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/rag-configs/{id}")
    print(res)
