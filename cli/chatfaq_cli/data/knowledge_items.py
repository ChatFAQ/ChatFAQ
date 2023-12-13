import typer
from rich import print
from typing_extensions import Annotated

app = typer.Typer(help="Knowledge items commands")


@app.command(rich_help_panel="Knowledge items commands")
def create(
    ctx: typer.Context,
    knowledge_base: Annotated[
        str, typer.Argument(help="The id/name of the knowledge base you wish to create an item for.")
    ],
    content: Annotated[str, typer.Argument(help="The content of the knowledge item.")],
    url: Annotated[str, typer.Argument(help="The url of the knowledge item.")],
    title: Annotated[str, typer.Argument(help="The title of the knowledge item.")] = None,
    section: Annotated[str, typer.Argument(help="The section of the knowledge item.")] = None,
    role: Annotated[str, typer.Argument(help="The role of the knowledge item.")] = None,
    page_number: Annotated[str, typer.Argument(help="The page number of the knowledge item.")] = None,
):
    """
    Creates a knowledge item.
    """
    r = ctx.parent.obj["r"].post(
        f"language-model/knowledge-items/",
        data={
            "knowledge_base": knowledge_base,
            "content": content,
            "url": url,
            "title": title,
            "section": section,
            "role": role,
            "page_number": page_number,
        }
    )
    print(r)


@app.command(rich_help_panel="Knowledge items commands", name="list")
def _list(
    ctx: typer.Context,
    knowledge_base: Annotated[
        str, typer.Argument(help="The id/name of the knowledge base you wish to list items from.")
    ],
):
    """
    List all knowledge items from a knowledge base.
    """
    arg = f"knowledge_base__id={knowledge_base}"
    if not knowledge_base.isnumeric():
        arg = f"knowledge_base__name={knowledge_base}"

    print(f"language-model/knowledge-items/?{arg}")
    print(ctx.parent.obj["r"].get(f"language-model/knowledge-items/?{arg}"))


@app.command(rich_help_panel="Knowledge items commands")
def update(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the knowledge item you wish to update.")],
    knowledge_base: Annotated[
        str, typer.Option(help="The id of the knowledge base you wish to create an item for.")
    ] = None,
    content: Annotated[str, typer.Option(help="The content of the knowledge item.")] = None,
    url: Annotated[str, typer.Option(help="The url of the knowledge item.")] = None,
    title: Annotated[str, typer.Option(help="The title of the knowledge item.")] = None,
    section: Annotated[str, typer.Option(help="The section of the knowledge item.")] = None,
    role: Annotated[str, typer.Option(help="The role of the knowledge item.")] = None,
    page_number: Annotated[str, typer.Option(help="The page number of the knowledge item.")] = None,
):
    """
    Updates a knowledge item.
    """
    data = {}
    if knowledge_base is not None:
        data["knowledge_base"] = knowledge_base
    if content is not None:
        data["content"] = content
    if url is not None:
        data["url"] = url
    if title is not None:
        data["title"] = title
    if section is not None:
        data["section"] = section
    if role is not None:
        data["role"] = role
    if page_number is not None:
        data["page_number"] = page_number

    r = ctx.parent.obj["r"].patch(
        f"language-model/knowledge-items/{id}/",
        data=data
    )
    print(r)


@app.command(rich_help_panel="Knowledge items commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the knowledge item you wish to delete.")],
):
    """
    Deletes a knowledge item.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/knowledge-items/{id}/")
    print(res)
