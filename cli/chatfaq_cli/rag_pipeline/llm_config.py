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
    Creates a LLM Config.
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


@app.command(rich_help_panel="LLM Config commands")
def update(
    ctx: typer.Context,
    id: Annotated[int, typer.Argument(help="The id of the LLM Config.")],
    name: Annotated[str, typer.Argument(help="The name of the LLM Config.")] = None,
    llm_type: Annotated[LLMTypeValues, typer.Argument(help="The type of the LLM to use.")] = None,
    llm_name: Annotated[str, typer.Argument(help="The name of the LLM to use. It can be a HuggingFace repo id, an OpenAI model id, etc.")] = None,
    ggml_llm_filename: Annotated[str, typer.Argument(help="The GGML filename of the model, if it is a GGML model.")] = None,
    model_config: Annotated[str, typer.Argument(help="The huggingface model config of the model, needed for GGML models.")] = None,
    load_in_8bit: Annotated[bool, typer.Argument(help="Whether to use the fast tokenizer or not.")] = None,
    use_fast_tokenizer: Annotated[bool, typer.Argument(help="Whether to use the fast tokenizer or not.")] = None,
    trust_remote_code_tokenizer: Annotated[bool, typer.Argument(help="Whether to trust the remote code of the tokenizer or not.")] = None,
    trust_remote_code_model: Annotated[bool, typer.Argument(help="Whether to trust the remote code of the model or not.")] = None,
    revision: Annotated[str, typer.Argument(help="The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models.")] = None,
    model_max_length: Annotated[int, typer.Argument(help="The maximum length of the model.")] = None,
):
    """
    Update a LLM Config.
    """
    data = {}
    if name is not None:
        data["name"] = name
    if llm_type is not None:
        data["llm_type"] = llm_type
    if llm_name is not None:
        data["llm_name"] = llm_name
    if ggml_llm_filename is not None:
        data["ggml_llm_filename"] = ggml_llm_filename
    if model_config is not None:
        data["model_config"] = model_config
    if load_in_8bit is not None:
        data["load_in_8bit"] = load_in_8bit
    if use_fast_tokenizer is not None:
        data["use_fast_tokenizer"] = use_fast_tokenizer
    if trust_remote_code_tokenizer is not None:
        data["trust_remote_code_tokenizer"] = trust_remote_code_tokenizer
    if trust_remote_code_model is not None:
        data["trust_remote_code_model"] = trust_remote_code_model
    if revision is not None:
        data["revision"] = revision
    if model_max_length is not None:
        data["model_max_length"] = model_max_length
    res = ctx.parent.obj["r"].patch(
        f"language-model/llm-configs/{id}/",
        data=data
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
