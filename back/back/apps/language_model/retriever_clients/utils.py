import re
from typing import Dict

from django.core.files.storage import default_storage


def extract_images_urls(text: str) -> Dict[str, str]:
    """
    Extracts the images paths from the text and returns a dictionary with the image path as key and the image url as value.
    """

    # The regex pattern to find the file paths.
    # It looks for a sequence of characters inside parentheses, preceded by a '!'
    pattern = r"!\[.*?\]\((.*?)\)"

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)

    # Create a dictionary with the image path as key and the image url as value
    image_urls = {}
    for match in matches:
        image_urls[match] = default_storage.url(match)

    return image_urls
