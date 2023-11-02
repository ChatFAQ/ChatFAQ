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


@app.command(rich_help_panel="Titles commands")
def create(
    ctx: typer.Context,
    knowledge_item: Annotated[int, typer.Argument(help="The id of the Knowledge Item")],
    title: Annotated[str, typer.Argument(help="The title of the Knowledge Item")],
):
    
    res = ctx.parent.obj["r"].post(
        f"language-model/auto-generated-titles/",
        data={
            "knowledge_item": knowledge_item,
            "title": title,
        }
    )
    print(res)


@app.command(rich_help_panel="Titles commands")
def update(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Auto Generated Title you want to update.")],
    title: Annotated[str, typer.Option(help="The title of the Knowledge Item")],
    knowledge_item: Annotated[int, typer.Option(help="The id of the Knowledge Item")] = None,
):
    """
    Updates a Auto Generated Title.
    """
    data = {}
    if knowledge_item is not None:
        data["knowledge_item"] = knowledge_item
    if title is not None:
        data["title"] = title
    res = ctx.parent.obj["r"].patch(f"language-model/auto-generated-titles/{id}/", data=data)
    print(res)


@app.command(rich_help_panel="Titles commands", name="list")
def _list(
    ctx: typer.Context,
    knowledge_item: Annotated[int, typer.Option(help="Filter by Knowledge Item")],
):
    """
    List all the Auto Generated Titles for a Knowledge Item.
    """
    params = {}
    if knowledge_item is not None:
        params["knowledge_item"] = knowledge_item
    res = ctx.parent.obj["r"].get(f"language-model/knowledge-items/{knowledge_item}/list-titles")
    print(res)


@app.command(rich_help_panel="Titles commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Auto Generated Title you want to delete.")],
):
    """
    Deletes a Auto Generated Title.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/auto-generated-titles/{id}/")
    print(res)

