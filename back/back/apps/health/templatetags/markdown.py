from django import template
from django.utils.safestring import SafeString

parse_markdown = __import__("markdown").markdown

register = template.Library()


@register.filter
def markdown(value):
    """
    Transforms a Markdown string into HTML

    Parameters
    ----------
    value
        The string to markdownify
    """

    return SafeString(parse_markdown(f"{value}"))
