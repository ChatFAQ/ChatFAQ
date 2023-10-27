import typer

from . import knowledge_items, knowledge_bases, intents, titles

app = typer.Typer(help="Data commands")
app.add_typer(knowledge_bases.app, name="knowledge_bases", help="Knowledge Bases commands")
app.add_typer(knowledge_items.app, name="knowledge_items", help="Knowledge Items commands")
app.add_typer(intents.app, name="intents", help="Intents commands")
app.add_typer(titles.app, name="titles", help="Autogen Titles commands")


if __name__ == "__main__":
    app()
