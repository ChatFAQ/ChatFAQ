import typer

from . import rag_config, llm_config, generation_config, prompt_config, retriever_config

app = typer.Typer(help="RAG Pipeline commands")
app.add_typer(rag_config.app, name="config", help="RAG Config commands")
app.add_typer(llm_config.app, name="llm", help="LLM Config commands")
app.add_typer(retriever_config.app, name="retriever", help="Retriever Config commands")
app.add_typer(prompt_config.app, name="prompt", help="Prompt Config commands")
app.add_typer(generation_config.app, name="generation", help="Generation Config commands")


if __name__ == "__main__":
    app()
