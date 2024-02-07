from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from .utils import Splitter, Strategy, verify_smart_splitter

app = typer.Typer(help="Knowledge bases commands")


@app.command(rich_help_panel="Knowledge Base commands")
def create_from_csv(
    ctx: typer.Context,
    name: Annotated[
        str, typer.Argument(help="The name you wish to give to the Knowledge Base.")
    ],
    source: Annotated[str, typer.Argument(help="The path to the CSV to upload.")],
    csv_header: Annotated[bool, typer.Option(help="Whether the csv file includes a header.")] = True,
    title_index_col: Annotated[int, typer.Option(help="The index of the column containing the title.")] = 0,
    content_index_col: Annotated[int, typer.Option(help="The index of the column containing the content.")] = 1,
    url_index_col: Annotated[int, typer.Option(help="The index of the column containing the url.")] = 2,
    section_index_col: Annotated[int, typer.Option(help="The index of the column containing the section.")] = 3,
    role_index_col: Annotated[int, typer.Option(help="The index of the column containing the role.")] = 4,
    page_number_index_col: Annotated[int, typer.Option(help="The index of the column containing the page number.")] = 5,
):
    """
    Create a new Knowledge Base.
    """
    res = ctx.parent.obj["r"].post(
        "language-model/knowledge-bases/",
        data={
            "name": name,
            "csv_header": csv_header,
            "title_index_col": title_index_col,
            "content_index_col": content_index_col,
            "url_index_col": url_index_col,
            "section_index_col": section_index_col,
            "role_index_col": role_index_col,
            "page_number_index_col": page_number_index_col,
        },
        files={"original_csv": open(source, "rb")},
    )
    print(res)


@app.command(rich_help_panel="Knowledge Base commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all Knowledge Bases.
    """
    print(ctx.parent.obj["r"].get("language-model/knowledge-bases/"))


@app.command(rich_help_panel="Knowledge Base commands")
def delete(
    ctx: typer.Context,
    id_name: Annotated[
        str, typer.Argument(help="The id/name of the Knowledge Base you wish to delete.")
    ],
):
    """
    Delete an existing Knowledge Base.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/knowledge-bases/{id_name}/", json=False)
    if res.ok:
        print(f"Knowledge Base {id_name} deleted.")
    else:
        print(res)


@app.command(rich_help_panel="Knowledge Base commands")
def download_csv(
    ctx: typer.Context,
    id_name: Annotated[str, typer.Argument(help="The id/name of the Knowledge Base you wish to download.")],
    download_path: Annotated[str, typer.Option(help="The path where you want to download the file.")] = None,
):
    """
    Download the Knowledge Base as a CSV file.
    """
    print("Downloading...")
    r = ctx.parent.obj["r"].get(
        f"language-model/knowledge-bases/{id_name}/download-csv", json=False
    )
    filename = r.headers["content-disposition"].split("attachment; filename=")[1]
    if not download_path:
        download_path = str(Path.home() / "Downloads" / filename)
    open(download_path, "wb").write(r.content)
    print(f"Downloaded into {download_path}")


@app.command(rich_help_panel="Knowledge Base commands")
def create_from_url(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the Knowledge Base to be created.")],
    language: Annotated[
        str, typer.Argument(help="The language of the Knowledge Base to be created.")
    ],
    url: Annotated[
        str, typer.Argument(help="The url to scrape and download the Knowledge Base from.")
    ],
    splitter: Annotated[
        Splitter,
        typer.Option(
            help="The splitter to use to split the text into knowledge units",
            case_sensitive=False,
        ),
    ] = Splitter.sentences,
    chunk_size: Annotated[
        int,
        typer.Option(
            help="The chunk size to use when splitting the text into knowledge units"
        ),
    ] = 128,
    chunk_overlap: Annotated[
        int,
        typer.Option(
            help="The chunk overlap to use when splitting the text into knowledge units"
        ),
    ] = 16,
    recursive: Annotated[
        bool,
        typer.Option(
            help="Whether to recursively scrape the website or not.",
            case_sensitive=False,
        ),
    ] = True,

):
    """
    Creates a new Knowledge Base from a url.
    """

    splitter = verify_smart_splitter(splitter)

    r = ctx.parent.obj["r"].post(
        f"language-model/knowledge-bases/",
        data={
            "name": name,
            "language": language,
            "original_url": url,
            "splitter": splitter.value,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "recursive": recursive,
            },
    )
    print(r)


@app.command(rich_help_panel="Knowledge Base commands")
def create_from_pdf(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the Knowledge Base to be created.")],
    language: Annotated[
        str, typer.Argument(help="The language of the Knowledge Base to be created.")
    ],
    pdf: Annotated[
        str,
        typer.Argument(
            help="The pdf file path to scrape and extract the Knowledge Base from."
        ),
    ],
    strategy: Annotated[
        Strategy,
        typer.Option(
            help="The strategy to use to extract the text from the pdf.",
            case_sensitive=False,
        ),
    ] = Strategy.fast,
    splitter: Annotated[
        Splitter,
        typer.Option(
            help="The splitter to use to split the text into knowledge units",
            case_sensitive=False,
        ),
    ] = Splitter.sentences,
    chunk_size: Annotated[
        int,
        typer.Option(
            help="The chunk size to use when splitting the text into knowledge units"
        ),
    ] = 128,
    chunk_overlap: Annotated[
        int,
        typer.Option(
            help="The chunk overlap to use when splitting the text into knowledge units"
        ),
    ] = 16,
):
    """
    Creates a new Knowledge Base from a pdf file.
    """

    splitter = verify_smart_splitter(splitter)

    r = ctx.parent.obj["r"].post(
        f"language-model/knowledge-bases/",
        data={
            "name": name,
            "language": language,
            "strategy": strategy.value,
            "splitter": splitter.value,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        },
        files={"original_pdf": open(pdf, "rb")},
    )
    print(r)
