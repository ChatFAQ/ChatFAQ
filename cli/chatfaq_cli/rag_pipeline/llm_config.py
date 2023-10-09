from enum import Enum
from typing import Annotated

import typer
from rich import print

app = typer.Typer(help="LLM Config commands")


class LLMTypeValues(str, Enum):
    local_cpu = "local_cpu"
    local_gpu = "local_gpu"
    vllm = "vllm"
    openai = "openai"


@app.command(rich_help_panel="LLM Config commands")
def create(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="The name of the LLM Config.")],
    llm_type: Annotated[LLMTypeValues, typer.Argument(help="The type of the LLM to use.")]=LLMTypeValues.openai,
    llm_name: Annotated[str, typer.Argument(help="The name of the LLM to use. It can be a HuggingFace repo id, an OpenAI model id, etc.")]="gpt2",
    ggml_llm_filename: Annotated[str, typer.Argument(help="The GGML filename of the model, if it is a GGML model.")]=None,
    model_config: Annotated[str, typer.Argument(help="The huggingface model config of the model, needed for GGML models.")]=None,
    load_in_8bit: Annotated[bool, typer.Argument(help="Whether to use the fast tokenizer or not.")]=False,
    use_fast_tokenizer: Annotated[bool, typer.Argument(help="Whether to use the fast tokenizer or not.")]=True,
    trust_remote_code_tokenizer: Annotated[bool, typer.Argument(help="Whether to trust the remote code of the tokenizer or not.")]=False,
    trust_remote_code_model: Annotated[bool, typer.Argument(help="Whether to trust the remote code of the model or not.")]=False,
    revision: Annotated[str, typer.Argument(help="The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models.")]="main",
    model_max_length: Annotated[int, typer.Argument(help="The maximum length of the model.")]=None,
):
    """
    List all LLM Configs.
    """
    res = ctx.parent.obj["r"].post(
        f"language-model/llm-configs/",
        data={
            "name": name,
            "llm_type": llm_type,
            "llm_name": llm_name,
            "ggml_llm_filename": ggml_llm_filename,
            "model_config": model_config,
            "load_in_8bit": load_in_8bit,
            "use_fast_tokenizer": use_fast_tokenizer,
            "trust_remote_code_tokenizer": trust_remote_code_tokenizer,
            "trust_remote_code_model": trust_remote_code_model,
            "revision": revision,
            "model_max_length": model_max_length
        }
    )
    print(res)


@app.command(rich_help_panel="LLM Config commands", name="list")
def _list(
    ctx: typer.Context,
):
    """
    List all LLM Configs.
    """
    print(ctx.parent.obj["r"].get(f"language-model/llm-configs/"))


@app.command(rich_help_panel="LLM Config commands")
def delete(
    ctx: typer.Context,
    id: Annotated[str, typer.Argument(help="The id of the LLM Config you want to delete.")],
):
    """
    Delete an existing LLM Config.
    """
    res = ctx.parent.obj["r"].delete(f"language-model/llm-configs/{id}")
    print(res)
