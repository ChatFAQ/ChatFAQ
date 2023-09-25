from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="LLM Config commands")


@app.command(rich_help_panel="LLM Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all LLM Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/llm-configs/"))


@app.command(rich_help_panel="LLM Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the LLM Config you want to delete.")],
):
    """
    Delete an existing LLM Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/llm-configs/{id}")
    print(res)
