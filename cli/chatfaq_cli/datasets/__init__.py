from pathlib import Path

import typer
from rich import print
from typing_extensions import Annotated

from . import items, utterances

app = typer.Typer(help="Datasets commands")
app.add_typer(items.app, name="items", help="Dataset's items commands")
app.add_typer(utterances.app, name="utterances", help="Items's utterances commands")


@app.command(rich_help_panel="Datasets commands")
def create(
    ctx: typer.Context,
    name: Annotated[
        str, typer.Argument(help="The name you wish to give to the dataset.")
    ],
    source: Annotated[
        str, typer.Argument(help="The path to the CSV, PDF or URL to upload.")
    ],
):
    """
    Create a new dataset.
    """
    res = ctx.parent.obj["r"].post(
        "language-model/datasets/",
        data={"name": name},
        files={"original_file": open(source, "rb")},
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
    language: Annotated[str, typer.Argument(help="The language of the dataset to be created.")],
    url: Annotated[str, typer.Argument(help="The url to scrape and download the dataset from.")],
):
    """
    Download the dataset as a CSV file.
    """
    print("Downloading...")
    r = ctx.parent.obj["r"].post(
        f"language-model/datasets/create_from_url/", data={"name": name, "language": language, "url": url}
    )
    print(r)


if __name__ == "__main__":
    app()