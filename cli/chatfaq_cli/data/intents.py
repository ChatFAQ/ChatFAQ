from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Knowledge bases commands")

@app.command(rich_help_panel="Intent commands")
def suggest_intents(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    Get new possible intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(f"language-model/intents/{kb_name}/suggest-intents/")
    print(res)


@app.command(rich_help_panel="Intent commands")
def generate_intents(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    Generate intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(f"language-model/intents/{kb_name}/generate-intents/")
    print(res)


@app.command(rich_help_panel="Knowledge Base commands")
def list(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    List intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].get(f"language-model/intents/{kb_name}/")
    print(res)
