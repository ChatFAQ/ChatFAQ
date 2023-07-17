import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Dataset's items commands")


@app.command(rich_help_panel="Dataset's items commands", name="list")
def _list(
    ctx: typer.Context,
    id: Annotated[
        str, typer.Argument(help="The id of the dataset you wish to list items from.")
    ],
):
    """
    List all items from a dataset.
    """
    print(ctx.parent.obj["r"].get(f"language-model/items/?dataset__id={id}"))
