from enum import Enum

import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Model commands")


@app.command(rich_help_panel="Model commands")
def create(
    ctx: typer.Context,
    name: Annotated[
        str, typer.Argument(help="The name you want to give to the model.")
    ],
    dataset: Annotated[
        str, typer.Argument(help="The name of the dataset associated with this model.")
    ],
    base_model: Annotated[
        str, typer.Option(help="The base model to use.")
    ] = "gpt2-medium"
):
    """
    Create a new model.
    """
    res = ctx.parent.obj["r"].post(
        "language-model/models/",
        data={"name": name, "dataset": dataset, "base_model": base_model},
    )
    print(res)


@app.command(rich_help_panel="Model commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the model you want to delete.")],
):
    """
    Delete an existing model.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/models/{id}")
    print(res)


@app.command(rich_help_panel="Model commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all the models.
    """
    print(ctx.parent.obj["r"].get("language-model/models/"))


if __name__ == "__main__":
    app()
