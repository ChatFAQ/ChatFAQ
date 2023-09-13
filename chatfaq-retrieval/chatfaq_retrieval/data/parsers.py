from typing import List, Optional, Union, BinaryIO, IO
from tempfile import SpooledTemporaryFile

import pandas as pd
from unstructured.documents.elements import (
    Element,
    Text,  # Uncategorized text
    Title,
)

from unstructured.partition.auto import partition_pdf, partition_html

from chatfaq_retrieval.data.models import Context


def is_strict_instance(obj, class_type):
    return isinstance(obj, class_type) and obj.__class__ is class_type


def is_header_or_footer(element: Element) -> bool:
    """
    Checks if an element is a header or footer.
    Parameters
    ----------
    element : Element
        An element to check.
    Returns
    -------
    bool
        True if the element is a header or footer, False otherwise.
    """
    # Check if the type matches typical header/footer types
    element = element.to_dict()
    if element["type"] not in ["Title", "UncategorizedText"]:
        return False

    # Get the Y-coordinate of the top left and bottom left of the potential header/footer
    y_top_left = element["metadata"]["coordinates"]["points"][0][1]
    y_bottom_left = element["metadata"]["coordinates"]["points"][1][1]

    # Page's height for reference
    page_height = element["metadata"]["coordinates"]["layout_height"]

    # Check if the element is within the top 10%, page header
    if y_top_left < 0.1 * page_height or y_bottom_left < 0.1 * page_height:
        return True
    # Check if the element is within the bottom 10% and the text is just a number, page footer
    if (
        y_top_left > 0.9 * page_height or y_bottom_left > 0.9 * page_height
    ) and element["text"].isdigit():
        return True

    return False


def parse_elements(
    elements: List[Element],
    file_type: str = "pdf",
    combine_section_under_n_chars: int = 500,
    new_after_n_chars: int = 1000,
) -> List[List[Element]]:
    """
    Parse a list of elements into sections following a set of rules based on the titles and length parameters.
    Parameters
    ----------
    elements : List[Element]
        A list of unstructured elements. Usually the ouput of a partition functions.
    file_type: str
        The type of file to parse. Can be 'pdf' or 'html'.
    combine_under_n_chars: int
        Combines elements (for example a series of titles) until a section reaches
        a length of n characters.
    new_after_n_chars: int
        Cuts off new sections once they reach a length of n characters
    Returns
    -------
    List[List[Element]]
        A list of sections, where each section is a list of elements.
    """

    sections = []
    section = []
    for element in elements:
        append = False

        if file_type == "pdf" and is_header_or_footer(element):
            continue

        if len(section) == 0:  # start of document
            append = True
        elif isinstance(section[-1], Title) and isinstance(
            element, Title
        ):  # Title -> Title : merge
            append = True
        elif is_strict_instance(section[-1], Text) and isinstance(
            element, Title
        ):  # Uncat Text -> Title : merge
            append = True
        elif isinstance(section[-1], Title) and not isinstance(
            element, Title
        ):  # Title -> Other : merge
            append = True
        elif not isinstance(section[-1], Title) and isinstance(
            element, Title
        ):  # Not Title -> Title : new section
            append = False
        elif not isinstance(section[-1], Title) and not isinstance(
            element, Title
        ):  # Not Title -> Not Title: merge
            append = True
        else:
            append = True

        # if the section is too short, just append
        section_length = sum([len(str(element)) for element in section])
        element_length = len(str(element))
        if (
            combine_section_under_n_chars != -1
            and (section_length + element_length) < combine_section_under_n_chars
        ):
            append = True
        if (
            new_after_n_chars != -1
            and (section_length + element_length) > new_after_n_chars
        ):
            append = False

        if append:
            section.append(element)
        else:
            sections.append(section)
            section = [element]

    sections.append(section)  # append the last section

    return sections


def transform_to_context(
    sections: List[List[Element]],
    file_type: str = "pdf",
) -> List[Context]:
    """
    Transforms a list of sections into a list of contexts and adds metadata.
    Parameters
    ----------
    sections : List[List[Element]]
        A list of sections, where each section is a list of elements.
    file_type: str
        The type of file that was used to generate the sections.
    Returns
    -------
    List[Context]
        A list of contexts.
    """

    sections_context = []
    prev_title = None  # save previous title to use if no title is found
    for ndx, section in enumerate(sections):
        title = None
        for element in section:
            if isinstance(element, Title):
                title = element.text
                break
        if title is None:  # if no title is found take the previous title
            title = prev_title
            if ndx == 0:  # first section and no title found
                # first 5 words as title
                title = " ".join([word for word in section[0].text.split()[:5]])

        section_context = Context(
            content="\n".join([element.text for element in section]), title=title
        )

        if file_type == "pdf":  # add page number
            section_context.page_number = section[0].metadata.page_number

        elif file_type == "html":  # add url
            url = (
                section[0].metadata.url
                if section[0].metadata.url
                else section[0].metadata.filename
            )  # use url if available, otherwise filename
            section_context.url = url

        if section_context.content.strip() != "":
            sections_context.append(section_context)

        prev_title = title  # save title for next section

    return sections_context


def parse_pdf(
    filename: str = "",
    file: Optional[Union[BinaryIO, SpooledTemporaryFile]] = None,
    strategy: str = "auto",
    combine_section_under_n_chars: int = 500,
    new_after_n_chars: int = 1000,
) -> List[Context]:
    """
    Parse a pdf file into sections.
    Parameters
    ----------
    filename : str
        The path to the pdf file.
    file : Optional[Union[BinaryIO, SpooledTemporaryFile]]
        The file object of the pdf file.
    strategy : str
        The strategy to use to parse the pdf file. Can be 'auto', 'fast', 'ocr' or 'high_res'.
    combine_section_under_n_chars: int
        Combines elements (for example a series of titles) until a section reaches
        a length of n characters.
    new_after_n_chars: int
        Cuts off new sections once they reach a length of n characters
    Returns
    -------
    List[Context]
        A list of contexts.
    """
    elements = partition_pdf(filename=filename, file=file, strategy=strategy)
    sections = parse_elements(
        elements,
        file_type="pdf",
        combine_section_under_n_chars=combine_section_under_n_chars,
        new_after_n_chars=new_after_n_chars,
    )

    contexts = transform_to_context(sections, file_type="pdf")

    return contexts


def parse_html(
    filename: Optional[str] = None,
    file: Optional[IO[bytes]] = None,
    text: Optional[str] = None,
    url: Optional[str] = None,
    encoding: Optional[str] = None,
    combine_section_under_n_chars: int = 500,
    new_after_n_chars: int = 1000,
) -> List[Context]:
    """
    Parse an html file into sections.
    Parameters
    ----------
    filename : Optional[str]
        The path to the html file.
    file : Optional[IO[bytes]]
        The file object of the html file.
    text : Optional[str]
        The text of the html file.
    url : Optional[str]
        The url of the html file.
    encoding : Optional[str]
        The encoding of the html file.
    combine_section_under_n_chars: int
        Combines elements (for example a series of titles) until a section reaches
        a length of n characters.
    new_after_n_chars: int
        Cuts off new sections once they reach a length of n characters
    Returns
    -------
    List[Context]
        A list of contexts.
    """
    elements = partition_html(
        filename=filename,
        file=file,
        text=text,
        url=url,
        encoding=encoding,
    )
    sections = parse_elements(
        elements,
        file_type="html",
        combine_section_under_n_chars=combine_section_under_n_chars,
        new_after_n_chars=new_after_n_chars,
    )

    contexts = transform_to_context(sections, file_type="html")

    return contexts
