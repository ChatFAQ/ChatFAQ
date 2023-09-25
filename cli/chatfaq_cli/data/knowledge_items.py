import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Knowledge items commands")


@app.command(rich_help_panel="Knowledge items commands", name="list")
def _list(
    ctx: typer.Context,
    id: Annotated[
        str, typer.Argument(help="The id of the knowledge base you wish to list items from.")
    ],
):
    """
    List all knowledge items from a knowledge base.
    """
    print(ctx.parent.obj["r"].get(f"language-model/knowledge-items/?knowledge_base__id={id}"))
