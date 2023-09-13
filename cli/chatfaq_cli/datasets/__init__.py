from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from . import items, utterances
from .utils import Splitter, Strategy, verify_smart_splitter

app = typer.Typer(help="Datasets commands")
app.add_typer(items.app, name="items", help="Dataset's items commands")
app.add_typer(utterances.app, name="utterances", help="Items's utterances commands")



@app.command(rich_help_panel="Datasets commands")
def create_from_csv(
    ctx: typer.Context,
    name: Annotated[
        str, typer.Argument(help="The name you wish to give to the dataset.")
    ],
    source: Annotated[str, typer.Argument(help="The path to the CSV to upload.")],
):
    """
    Create a new dataset.
    """
    res = ctx.parent.obj["r"].post(
        "language-model/datasets/",
        data={"name": name},
        files={"original_csv": open(source, "rb")},
    )
    print(res)


@app.command(rich_help_panel="Datasets commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all datasets.
    """
    print(ctx.parent.obj["r"].get("language-model/datasets/"))


@app.command(rich_help_panel="Datasets commands")
def delete(
    ctx: typer.Context,
    id: Annotated[
        str, typer.Argument(help="The id of the dataset you wish to delete.")
    ],
):
    """
    Delete an existing dataset.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/datasets/{id}/", json=False)
    if res.ok:
        print(f"Dataset {id} deleted.")
    else:
        print(res)


@app.command(rich_help_panel="Datasets commands")
def download_csv(
    ctx: typer.Context,
    id: Annotated[
        str, typer.Argument(help="The id of the dataset you wish to download.")
    ],
    download_path: Annotated[
        str, typer.Option(help="The path where you want to download the file.")
    ] = None,
):
    """
    Download the dataset as a CSV file.
    """
    print("Downloading...")
    r = ctx.parent.obj["r"].get(
        f"language-model/datasets/{id}/download_csv", json=False
    )
    filename = r.headers["content-disposition"].split("attachment; filename=")[1]
    if not download_path:
        download_path = str(Path.home() / "Downloads" / filename)
    open(download_path, "wb").write(r.content)
    print(f"Downloaded into {download_path}")


@app.command(rich_help_panel="Datasets commands")
def create_from_url(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the dataset to be created.")],
    language: Annotated[
        str, typer.Argument(help="The language of the dataset to be created.")
    ],
    url: Annotated[
        str, typer.Argument(help="The url to scrape and download the dataset from.")
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
    Creates a new dataset from a url.
    """

    splitter = verify_smart_splitter(splitter)

    r = ctx.parent.obj["r"].post(
        f"language-model/datasets/",
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


@app.command(rich_help_panel="Datasets commands")
def create_from_pdf(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the dataset to be created.")],
    language: Annotated[
        str, typer.Argument(help="The language of the dataset to be created.")
    ],
    pdf: Annotated[
        str,
        typer.Argument(
            help="The pdf file path to scrape and extract the dataset from."
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
    Creates a new dataset from a pdf file.
    """

    splitter = verify_smart_splitter(splitter)

    r = ctx.parent.obj["r"].post(
        f"language-model/datasets/",
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


if __name__ == "__main__":
    app()
