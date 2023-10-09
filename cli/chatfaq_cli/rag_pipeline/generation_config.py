from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Generation Config commands")


@app.command(rich_help_panel="Generation Config commands")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the Generation Config.")],
    top_k: Annotated[int, typer.Argument(help="The number of tokens to consider for the top-k sampling, by default 50")]=50,
    top_p: Annotated[float, typer.Argument(help="The cumulative probability for the top-p sampling, by default 1.0")]=1.0,
    temperature: Annotated[float, typer.Argument(help="The temperature for the sampling, by default 1.0")]=1.0,
    repetition_penalty: Annotated[float, typer.Argument(help="The repetition penalty for the sampling, by default 1.0")]=1.0,
    seed: Annotated[int, typer.Argument(help="The seed for the sampling, by default 42")]=42,
    max_new_tokens: Annotated[int, typer.Argument(help="The maximum number of new tokens to generate, by default 256")]=256,
):
    """
    Creates a Generation Configs.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/prompt-configs/",
        data={
            "name": name,
            "top_k": top_k,
            "top_p": top_p,
            "temperature": temperature,
            "repetition_penalty": repetition_penalty,
            "seed": seed,
            "max_new_tokens": max_new_tokens,
        }
    )
    print(res)


@app.command(rich_help_panel="Generation Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Generation Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/generation-configs/"))


@app.command(rich_help_panel="Generation Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Generation Config you want to delete.")],
):
    """
    Delete an existing Generation Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/generation-configs/{id}")
    print(res)
