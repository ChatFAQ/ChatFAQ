import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Auto Generated Titles commands")


@app.command(rich_help_panel="Auto Generated Titles commands")
def create(
    ctx: typer.Context,
    auto_generated_title_id: Annotated[
        str,
        typer.Argument(help="The id of the Knowledge Item you wish to create an Auto Generated Title for."),
    ],
    title: Annotated[str, typer.Argument(help="The text of the Auto Generated Title.")],
):
    """
    Create a new Auto Generated Title.
    """

    res = ctx.parent.obj["r"].post(
        "language-model/auto-generated-titles/", data={"item": auto_generated_title_id, "title": title}
    )
    print(res)


@app.command(rich_help_panel="Auto Generated Titles commands", name="list")
def _list(
    ctx: typer.Context,
    id: Annotated[
        str, typer.Argument(help="The id of the Knowledge Item you wish to create an Auto Generated Title for."),
    ],
):
    """
    List all Auto Generated Titles from a Knowledge Item.
    """
    print(ctx.parent.obj["r"].get(f"language-model/auto-generated-titles/?knowledge_item__id={id}"))
