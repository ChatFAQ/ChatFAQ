from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Retriever Config commands")


@app.command(rich_help_panel="Retriever Config commands")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the Retriever Config.")],
    model_name: Annotated[str, typer.Argument(help="The name of the Retriever model to use. It must be a HuggingFace repo id.")]="intfloat/e5-small-v2",
    batch_size: Annotated[int, typer.Argument(help="The batch size to use for the Retriever.")]=1,
    device: Annotated[str, typer.Argument(help="The device to use for the Retriever.")]="cpu",

):
    """
    Creates a Retriever Configs.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/retriever-configs/",
        data={
            "name": name,
            "model_name": model_name,
            "batch_size": batch_size,
            "device": device,
        }
    )
    print(res)


@app.command(rich_help_panel="Retriever Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Retriever Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/retriever-configs/"))


@app.command(rich_help_panel="Retriever Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Retriever Config you want to delete.")],
):
    """
    Delete an existing Retriever Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/retriever-configs/{id}")
    print(res)
