from enum import Enum
import typer

class Strategy(str, Enum):
    """
    The strategy to use to extract the text from the pdf.
    https://unstructured-io.github.io/unstructured/bricks/partition.html#partition-pdf
    """
    auto = "auto"
    fast = "fast"
    ocr_only = "ocr_only"
    hi_res = "hi_res"

class Splitter(str, Enum):
    """
    The splitter to use to split the text into knowledge units
    """
    words = "words"
    sentences = "sentences"
    tokens = "tokens"
    smart = "smart"

def verify_smart_splitter(splitter: Splitter):
    """
    Verify if the user wants to use the smart splitter, which is expensive and slow.
    """
    if splitter == Splitter.smart:
        splitter = typer.prompt(
            "Splitter smart is expensive and slow. Are you sure you want to use it? [y/N]",
            default="n",
        )
        if splitter.lower() == "y":
            splitter = Splitter.smart
        else:
            splitter = typer.prompt(
                "Choose another splitter: [words/sentences/tokens]",
                default="sentences",
            )

            splitter = Splitter(splitter)
            print(splitter)
    return splitter