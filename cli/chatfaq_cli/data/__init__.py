import typer

from . import knowledge_items, auto_generated_titles, knowledge_bases, intents

app = typer.Typer(help="Data commands")
app.add_typer(knowledge_bases.app, name="knowledge_bases", help="Knowledge Bases commands")
app.add_typer(knowledge_items.app, name="knowledge_items", help="Knowledge Items commands")
app.add_typer(auto_generated_titles.app, name="auto_generated_titles", help="Auto Generated Titles commands")
app.add_typer(intents.app, name="intents", help="Intents commands")


if __name__ == "__main__":
    app()
