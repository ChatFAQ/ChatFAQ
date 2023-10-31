from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Knowledge bases commands")


@app.command(rich_help_panel="Generation Intents commands")
def suggest(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    Get suggested new possible intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(f"language-model/intents/{kb_name}/suggest-intents/")
    print(res)


@app.command(rich_help_panel="Generation Intents commands")
def generate(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    Generate existing intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/intents/{kb_name}/generate-intents/"
    )
    print(res)


@app.command(rich_help_panel="Intents commands")
def create(
    ctx: typer.Context,
    intent: Annotated[str, typer.Argument(help="The intent name")],
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
):
    """
    Create an intent.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/intents/",
        data={
            "intent_name": intent,
            "valid": True,
            "knowledge_base": kb_name,
        },
    )
    print(res)


@app.command(rich_help_panel="Intents commands")
def update(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Intent you want to update.")],
    intent: Annotated[str, typer.Option(help="The intent name")],
):
    """
    Updates an intent.
    """
    data = {}
    if intent is not None:
        data["intent_name"] = intent
    res = ctx.parent.obj["r"].patch(f"language-model/intents/{id}/", data=data)
    print(res)


@app.command(rich_help_panel="Intents commands", name="list")
def _list(
    ctx: typer.Context,
    kb_name: Annotated[str, typer.Argument(help="The name of the Knowledge Base")],
    existing: Annotated[bool, typer.Option(help="List only existing intents")] = False,
    suggested: Annotated[
        bool, typer.Option(help="List only suggested intents")
    ] = False,
):
    """
    List intents from a Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/knowledge-bases/{kb_name}/list-intents/",
        data={
            "existing": existing,
            "suggested": suggested,
        },
    )
    print(res)


@app.command(rich_help_panel="Intents commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Intent you want to delete.")],
):
    """
    Delete an intent.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/intents/{id}/")
    print(res)
