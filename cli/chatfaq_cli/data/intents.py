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
    # if both are false, list all
    if not existing and not suggested:
        existing = True
        suggested = True
    res = ctx.parent.obj["r"].post(
        f"language-model/knowledge-bases/{kb_name}/list-intents/",
        data={
            "existing": existing,
            "suggested": suggested,
        },
    )
    print(res)

@app.command(rich_help_panel="Intents commands", name="list-kis")
def list_intents_knowledge_items(
    ctx: typer.Context,
    intent_id: Annotated[str, typer.Argument(help="The id of the Intent")],
):
    """
    List Knowledge Items from an Intent.
    """
    res = ctx.parent.obj["r"].get(
        f"language-model/intents/{intent_id}/list-knowledge-items/",
    )
    print(res)

@app.command(rich_help_panel="Intents commands", name="list-intents-by-ki")
def list_intents_by_knowledge_item(
    ctx: typer.Context,
    ki_id: Annotated[str, typer.Argument(help="The id of the Knowledge Item")],
):
    """
    List a Knowledge Item's intents.
    """
    res = ctx.parent.obj["r"].get(
        f"language-model/knowledge-items/{ki_id}/list-intents/",
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
