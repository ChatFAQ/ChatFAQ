from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="RAG Config commands")


@app.command(rich_help_panel="RAG Config commands")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the RAG Config you want to create.")],
    knowledge_base: Annotated[str, typer.Argument(help="The id of the Knowledge Base you want to use.")],
    llm_config: Annotated[str, typer.Argument(help="The id of the LLM Config you want to use.")],
    prompt_config: Annotated[str, typer.Argument(help="The id of the Prompt Config you want to use.")],
    generation_config: Annotated[str, typer.Argument(help="The id of the Generation Config you want to use.")],
    retriever_config: Annotated[str, typer.Argument(help="The id of the Retriever Config you want to use.")],
):
    """
    Creates a RAG Configs.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/rag-configs/",
        data={
            "name": name,
            "knowledge_base": knowledge_base,
            "llm_config": llm_config,
            "retriever_config": retriever_config,
            "prompt_config": prompt_config,
            "generation_config": generation_config,
        }
    )
    print(res)


@app.command(rich_help_panel="RAG Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all RAG Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/rag-configs/"))


@app.command(rich_help_panel="RAG commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the RAG you want to delete.")],
):
    """
    Delete an existing RAG.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/rag-configs/{id}")
    print(res)
