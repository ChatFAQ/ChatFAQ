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
    Creates a Prompt Config.
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


@app.command(rich_help_panel="Prompt Config commands")
def update(
    ctx: typer.Context,
    id: Annotated[int, typer.Argument(help="The id of the Prompt Config.")],
    name: Annotated[str, typer.Argument(help="The name of the Prompt Config.")] = None,
    system_prefix: Annotated[str, typer.Argument(help="The prefix to indicate instructions for the LLM.")] = None,
    system_tag: Annotated[str, typer.Argument(help="The tag to indicate the start of the system prefix for the LLM.")] = None,
    system_end: Annotated[str, typer.Argument(help="The tag to indicate the end of the system prefix for the LLM.")] = None,
    user_tag: Annotated[str, typer.Argument(help="The tag to indicate the start of the user input.")] = None,
    user_end: Annotated[str, typer.Argument(help="The tag to indicate the end of the user input.")] = None,
    assistant_tag: Annotated[str, typer.Argument(help="The tag to indicate the start of the assistant output.")] = None,
    assistant_end: Annotated[str, typer.Argument(help="The tag to indicate the end of the assistant output.")] = None,
    n_contexts_to_use: Annotated[int, typer.Argument(help="The number of contexts to use, by default 3")] = None,
):
    """
    Updates a Prompt Configs.
    """
    data = {}
    if name is not None:
        data["name"] = name
    if system_prefix is not None:
        data["system_prefix"] = system_prefix
    if system_tag is not None:
        data["system_tag"] = system_tag
    if system_end is not None:
        data["system_end"] = system_end
    if user_tag is not None:
        data["user_tag"] = user_tag
    if user_end is not None:
        data["user_end"] = user_end
    if assistant_tag is not None:
        data["assistant_tag"] = assistant_tag
    if assistant_end is not None:
        data["assistant_end"] = assistant_end
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
