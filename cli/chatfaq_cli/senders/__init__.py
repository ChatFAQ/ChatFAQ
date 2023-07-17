import typer
from rich import print

app = typer.Typer(help="Senders commands")


@app.command(rich_help_panel="Senders commands", name="list")
def _list(ctx: typer.Context):
    """
    It returns a list of all the human senders.
    """
    print(ctx.parent.obj["r"].get("broker/senders"))


if __name__ == "__main__":
    app()
