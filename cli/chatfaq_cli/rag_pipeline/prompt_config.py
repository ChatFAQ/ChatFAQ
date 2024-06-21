from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Prompt Config commands")


@app.command(rich_help_panel="Prompt Config commands")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the Prompt Config.")],
    system_prompt: Annotated[str, typer.Argument(help="The prefix to indicate instructions for the LLM.")]="",
    n_contexts_to_use: Annotated[int, typer.Argument(help="The number of contexts to use, by default 3")]=3,
):
    """
    Creates a Prompt Config.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/prompt-configs/",
        data={
            "name": name,
            "system_prompt": system_prompt,
            "n_contexts_to_use": n_contexts_to_use
        }
    )
    print(res)


@app.command(rich_help_panel="Prompt Config commands")
def update(
    ctx: typer.Context,
    id: Annotated[int, typer.Argument(help="The id of the Prompt Config.")],
    name: Annotated[str, typer.Option(help="The name of the Prompt Config.")] = None,
    system_prompt: Annotated[str, typer.Option(help="The prefix to indicate instructions for the LLM.")] = None,
    n_contexts_to_use: Annotated[int, typer.Option(help="The number of contexts to use, by default 3")] = None,
):
    """
    Updates a Prompt Configs.
    """
    data = {}
    if name is not None:
        data["name"] = name
    if system_prompt is not None:
        data["system_prompt"] = system_prompt
    if n_contexts_to_use is not None:
        data["n_contexts_to_use"] = n_contexts_to_use
    res = ctx.parent.obj["r"].patch(
        f"language-model/prompt-configs/{id}/",
        data=data
    )
    print(res)


@app.command(rich_help_panel="Prompt Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Prompt Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/prompt-configs/"))


@app.command(rich_help_panel="Prompt Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the Prompt Config you want to delete.")],
):
    """
    Delete an existing Prompt Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/prompt-configs/{id}")
    print(res)
