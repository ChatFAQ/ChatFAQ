from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Knowledge bases commands")

@app.command(rich_help_panel="Auto generate titles commands")
def generate(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
    n_titles: Annotated[int, typer.Option(help="The number of titles to generate for each Knowledge Item")] = 10,
):
    """
    Generate titles for a Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(f"language-model/auto-generated-titles/{kb_name}/generate/", data={"n_titles": n_titles})
    print(res)
