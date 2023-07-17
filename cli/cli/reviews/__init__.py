from enum import Enum
from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="Review commands")


class ReviewValues(str, Enum):
    positive = "positive"
    negative = "negative"


@app.command(rich_help_panel="Review commands")
def create(
    ctx: typer.Context,
    message_id: Annotated[
        int,
        typer.Argument(
            help="The id of the message you are going to create the feedback to."
        ),
    ],
    value: Annotated[ReviewValues, typer.Argument(help="The value of the feedback.")],
    review: Annotated[
        str,
        typer.Argument(
            help="In case of a negative review, the correct answer it should have been"
        ),
    ],
):
    """
    Create a new review.
    """
    print(
        ctx.parent.obj["r"].post(
            "broker/admin-reviews/",
            data={"message_id": message_id, "value": value, "review": review},
        )
    )


@app.command(rich_help_panel="Review commands", name="list")
def _list(ctx: typer.Context):
    """
    It returns all the reviews being made
    """
    print(ctx.parent.obj["r"].get("broker/admin-reviews"))


if __name__ == "__main__":
    app()
