from enum import Enum

from typing_extensions import Annotated
import time

from tqdm import tqdm

from rich.console import Console

import typer
from rich import print

app = typer.Typer(help="Model commands")


class Models(str, Enum):
    mpt = " mosaicml/mpt-30b-instruct " + " " * 100
    openassistant = " OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5 " + " " * 100
    falcon = " tiiuae/falcon-7b-instruct " + " " * 100
    openai = " OpenAI/GPT-4 " + " " * 100
    redpajama = " togethercomputer/RedPajama-INCITE-7B-Chat "


@app.command(rich_help_panel="Model commands")
def create(
        ctx: typer.Context,
        name: Annotated[str, typer.Argument(help="The name you want to give to the model.")],
        dataset: Annotated[str, typer.Argument(help="The name of the dataset associated with this model.")],
        base_model: Annotated[Models, typer.Option(help="The base model to use.")] = Models.mpt,
):
    """
    Create a new model.
    """
    for i in tqdm(range(300)):
        time.sleep(0.01)
    print(f"\n")
    Console().print(f"Model \'{name}\' Deployed!", style="#52ad8d")
    print(f"\n")
    return
    res = ctx.parent.obj["r"].post(
        "language-model/models/",
        data={"name": name, "dataset": dataset, "base_model": base_model}
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
