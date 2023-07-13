import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Items's utterances commands")


@app.command(rich_help_panel="Items's utterances commands")
def create(
        ctx: typer.Context,
        item_id: Annotated[str, typer.Argument(help="The id of the item you wish to create an utterance for.")],
        intent: Annotated[str, typer.Argument(help="The text of the utterance.")],
):
    """
    Create a new utterance.
    """

    res = ctx.parent.obj["r"].post(
        "language-model/utterances/",
        data={"item": item_id, "intent": intent}
    )
    print(res)


@app.command(rich_help_panel="Items's utterances commands", name="list")
def _list(
        ctx: typer.Context,
        id: Annotated[str, typer.Argument(help="The id of the item you wish to list utterances from.")],
):
    """
    List all utterances from an item.
    """
    print(ctx.parent.obj["r"].get(f"language-model/utterances/?item__id={id}"))
