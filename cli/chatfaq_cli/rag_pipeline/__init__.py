import typer

from . import rag_config, llm_config, generation_config, prompt_config

app = typer.Typer(help="RAG Pipeline commands")
app.add_typer(rag_config.app, name="rag_config", help="RAG Config commands")
app.add_typer(llm_config.app, name="llm_config", help="LLM Config commands")
app.add_typer(prompt_config.app, name="retriever_config", help="Retriever Config commands")
app.add_typer(prompt_config.app, name="prompt_config", help="Prompt Config commands")
app.add_typer(generation_config.app, name="generation_config", help="Generation Config commands")


if __name__ == "__main__":
    app()
