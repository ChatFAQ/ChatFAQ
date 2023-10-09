from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Prompt Config commands")


@app.command(rich_help_panel="Prompt Config commands")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the Prompt Config.")],
    system_prefix: Annotated[str, typer.Argument(help="The prefix to indicate instructions for the LLM.")]="",
    system_tag: Annotated[str, typer.Argument(help="The tag to indicate the start of the system prefix for the LLM.")]="",
    system_end: Annotated[str, typer.Argument(help="The tag to indicate the end of the system prefix for the LLM.")]="",
    user_tag: Annotated[str, typer.Argument(help="The tag to indicate the start of the user input.")]="<|prompt|>",
    user_end: Annotated[str, typer.Argument(help="The tag to indicate the end of the user input.")]="",
    assistant_tag: Annotated[str, typer.Argument(help="The tag to indicate the start of the assistant output.")]="<|answer|>",
    assistant_end: Annotated[str, typer.Argument(help="The tag to indicate the end of the assistant output.")]="",
    n_contexts_to_use: Annotated[int, typer.Argument(help="The number of contexts to use, by default 3")]=3,
):
    """
    Creates a Prompt Configs.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/prompt-configs/",
        data={
            "name": name,
            "system_prefix": system_prefix,
            "system_tag": system_tag,
            "system_end": system_end,
            "user_tag": user_tag,
            "user_end": user_end,
            "assistant_tag": assistant_tag,
            "assistant_end": assistant_end,
            "n_contexts_to_use": n_contexts_to_use
        }
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
