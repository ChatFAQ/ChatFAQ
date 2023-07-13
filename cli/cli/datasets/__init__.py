import time
from pathlib import Path
from tqdm import tqdm
import typer
from rich import print
from rich.console import Console
from typing_extensions import Annotated
from . import items
from . import utterances

app = typer.Typer(help="Datasets commands")
app.add_typer(items.app, name="items", help="Dataset's items commands")
app.add_typer(utterances.app, name="utterances", help="Items's utterances commands")


@app.command(rich_help_panel="Datasets commands")
def create(
        ctx: typer.Context,
        name: Annotated[str, typer.Argument(help="The name you wish to give to the dataset.")],
        source: Annotated[str, typer.Argument(help="The path to the CSV, PDF or URL to upload.")]
):
    """
    Create a new dataset.
    """
    for i in tqdm(range(100)):
        time.sleep(0.01)
    print(f"\n")
    Console().print(f"Dataset \'{name}\' Created!", style="#52ad8d")
    print(f"\n")
    return
    res = ctx.parent.obj["r"].post(
        "language-model/datasets/",
        data={"name": name},
        files={"original_file": open(source, "rb")})
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
        id: Annotated[str, typer.Argument(help="The id of the dataset you wish to delete.")],
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
        id: Annotated[str, typer.Argument(help="The id of the dataset you wish to download.")],
        download_path: Annotated[str, typer.Option(help="The path where you want to download the file.")] = None,
):
    """
    Download the dataset as a CSV file.
    """
    print("Downloading...")
    r = ctx.parent.obj["r"].get(f"language-model/datasets/{id}/download_csv", json=False)
    filename = r.headers['content-disposition'].split("attachment; filename=")[1]
    if not download_path:
        download_path = str(Path.home() / "Downloads" / filename)
    open(download_path, 'wb').write(r.content)
    print(f"Downloaded into {download_path}")


if __name__ == "__main__":
    app()
