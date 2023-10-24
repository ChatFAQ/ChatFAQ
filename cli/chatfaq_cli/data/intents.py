from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Knowledge bases commands")

@app.command(rich_help_panel="Intent commands")
def get_new_intents(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    Get new possible intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].get(f"language-model/knowledge-bases/{kb_name}/get-new-intents/")
    print(res)