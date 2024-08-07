import re
from typing import List, Tuple
from src.core.htmlnode import ParentNode, LeafNode
from src.core.textnode import TextNode
import src.core.text_functions as tf

BLOCK_TYPE_PARAGRAPH = "paragraph"
BLOCK_TYPE_HEADING = "heading"
BLOCK_TYPE_CODE = "code"
BLOCK_TYPE_QUOTE = "quote"
BLOCK_TYPE_UNORD_LIST = "unordered_list"
BLOCK_TYPE_ORD_LIST = "ordered_list"


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    """
    Extract all markdown image references from a given text.

    Args:
        text (str): The input text containing markdown image references.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains the alt text and the URL of an image.

    Example:
        >>> extract_markdown_images("This is an image ![alt text](http://example.com/image.jpg).")
        [('alt text', 'http://example.com/image.jpg')]
    """
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    """
    Extract all markdown links from a given text.

    Args:
        text (str): The input text containing markdown links.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains the link text and the URL.

    Example:
        >>> extract_markdown_links("This is a [link](http://example.com).")
        [('link', 'http://example.com')]
    """
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)


def get_codeblock_indices(text: str) -> List[Tuple[int, int]]:
    """
    Identify the start and end indices of all code blocks in a Markdown string.

    This function searches for code blocks in the provided Markdown text. Code blocks
    are defined as text wrapped in triple backticks (```).

    Parameters:
    text (str): The raw Markdown string representing a full document.

    Returns:
    List[Tuple[int, int]]: A list of tuples, where each tuple contains the start and
                           end indices of a code block in the text.
    """
    indices = list()
    matches = re.finditer(r"^`{3}\n?[\s\S]*?\n?^`{3}", text, re.MULTILINE)
    for match in matches:
        indices.append((match.start(0), match.end(0)))
    return indices


def get_non_codeblocks(text: str) -> List[str]:
    """
    Extract non-code blocks from a given text by splitting on newlines.

    This function splits the input text into blocks by newlines. It strips any leading
    or trailing whitespace from each block and removes any empty blocks created by
    excessive newlines.

    Parameters:
    text (str): The input text string to be split into non-code blocks.

    Returns:
    List[str]: A list of non-code block strings, with leading and trailing whitespace removed.
    """
    blocks = list()
    lines = text.split("\n")
    current_block = []

    def add_block():
        if current_block:
            blocks.append("\n".join(current_block).strip())
            current_block.clear()

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            add_block()
        else:
            current_block.append(stripped_line)

    add_block()  # Add the last block if there's any

    return blocks


def markdown_to_blocks(text: str) -> List[str]:
    """
    Convert a raw Markdown string into a list of block strings.

    This function splits the input Markdown string into distinct blocks, where each
    block is separated by one or more newlines. It handles code blocks separately,
    ensuring they are not split incorrectly, and processes non-code blocks to strip
    any leading or trailing whitespace and remove any empty blocks created by
    excessive newlines.

    Parameters:
    text (str): The raw Markdown string representing a full document.

    Returns:
    List[str]: A list of block strings, with leading and trailing whitespace removed.
    """
    blocks = list()
    current_pos = 0
    codeblock_indices = get_codeblock_indices(text)
    if codeblock_indices:
        for c_start, c_end in codeblock_indices:
            blocks.extend(get_non_codeblocks(text[current_pos:c_start]))
            blocks.append(text[c_start:c_end])
            current_pos = c_end
        blocks.extend(get_non_codeblocks(text[current_pos:]))
    else:
        blocks = get_non_codeblocks(text)

    return blocks


def get_markdown_block_type(block: str) -> str:
    """
    Determine the type of a Markdown block.

    This function takes a block of Markdown text and returns its type based on
    predefined constants for various Markdown block elements (e.g., heading, code, quote, lists).

    Parameters:
    block (str): A string representing a single block of Markdown text.

    Returns:
    str: A string representing the type of the Markdown block, which can be one of the following:
         - "heading"
         - "code"
         - "quote"
         - "unordered_list"
         - "ordered_list"
         - "paragraph"

    Examples:
    >>> block_to_block_type("# Heading")
    'heading'
    >>> block_to_block_type("```code block```")
    'code'
    >>> block_to_block_type("> Quote")
    'quote'
    >>> block_to_block_type("* Unordered list item")
    'unordered_list'
    >>> block_to_block_type("1. Ordered list item")
    'ordered_list'
    >>> block_to_block_type("Just a paragraph.")
    'paragraph'
    """
    if re.match(r"^#{1,6}\s", block):
        return BLOCK_TYPE_HEADING
    elif block.startswith("```") and block.endswith("```"):
        return BLOCK_TYPE_CODE
    elif all(line.startswith(">") for line in block.split("\n")):
        return BLOCK_TYPE_QUOTE
    elif all(re.match(r"^[*-]\s", line) for line in block.split("\n")):
        return BLOCK_TYPE_UNORD_LIST
    elif all(re.match(r"^\d+\.\s", line) for line in block.split("\n")):
        lines = block.split("\n")
        for i, line in enumerate(lines):
            if int(line.split(".")[0]) != i + 1:
                return BLOCK_TYPE_PARAGRAPH
        return BLOCK_TYPE_ORD_LIST
    return BLOCK_TYPE_PARAGRAPH


def markdown_heading_to_text_node(text: str) -> List[TextNode]:
    """
    Convert a Markdown heading line to a list of TextNode objects.

    This function checks if the input text is a Markdown heading (denoted by 1 to 6 leading '#' characters followed by a space).
    If it is a heading, the '#' characters are removed, and the remaining text is processed. If it is not a heading, the text
    is processed as is.

    Args:
        text (str): The Markdown text to be converted.

    Returns:
        List[TextNode]: A list of TextNode objects representing the input text.
    """
    if re.match(r"^#{1,6}\s", text):
        return tf.text_line_to_text_nodes(text=text.replace("#", "").lstrip())
    else:
        return tf.text_line_to_text_nodes(text=text)


def markdown_quote_to_text_node(text: str) -> List[TextNode]:
    """
       Convert a Markdown quote block to a list of TextNode objects.

    This function processes the input text, removes the Markdown quote syntax ("> "),
    and converts the resulting text into a list of TextNode objects.

    Args:
        text (str): The Markdown quote block to be converted.

    Returns:
        List[TextNode]: A list of TextNode objects representing the text in the quote block.

    Raises:
        NotImplementedError: If the quote block is empty.
    """
    if text == "> ":
        raise NotImplementedError("Empty quotes not supported")
    return tf.text_line_to_text_nodes(re.sub(r"^>\s", "", text, flags=re.MULTILINE))


def markdown_unord_list_to_text_node(text: str) -> List[List[TextNode]]:
    """
    Convert a Markdown unordered list to a list of lists of TextNode objects.

    This function processes the input text, removes the Markdown list syntax ("* " or "- "),
    and converts each list item into a list of TextNode objects.

    Args:
        text (str): The Markdown unordered list to be converted.

    Returns:
        List[List[TextNode]]: A list of lists of TextNode objects representing the text in the unordered list.

    Raises:
        NotImplementedError: If the unordered list contains an empty item.
    """
    nodes = list()
    text_without_delimiter = re.sub(r"^[*-]\s", "", text, flags=re.MULTILINE)
    for line in text_without_delimiter.split("\n"):
        if not line:
            raise NotImplementedError("Empty lists not supported")
        nodes.append(tf.text_line_to_text_nodes(line))
    return nodes


def markdown_ord_list_to_text_node(text: str) -> List[List[TextNode]]:
    """
    Convert a Markdown ordered list to a list of lists of TextNode objects.

    This function processes the input text, removes the Markdown list syntax ("1. ", "2. ", and so on..),
    and converts each list item into a list of TextNode objects.

    Args:
        text (str): The Markdown ordered list to be converted.

    Returns:
        List[List[TextNode]]: A list of lists of TextNode objects representing the text in the ordered list.

    Raises:
        NotImplementedError: If the ordered list contains an empty item.
    """
    nodes = list()
    text_without_delimiter = re.sub(r"^\d+\.\s", "", text, flags=re.MULTILINE)
    for line in text_without_delimiter.split("\n"):
        if not line:
            raise NotImplementedError("Empty lists not supported")
        nodes.append(tf.text_line_to_text_nodes(line))
    return nodes


def markdown_paragraph_to_text_node(text: str) -> List[TextNode]:
    """
    Convert a Markdown paragraph to a list of TextNode objects.

    Args:
        text (str): The Markdown paragraph to convert.

    Returns:
        List[TextNode]: A list of TextNode objects representing the Markdown paragraph.

    Raises:
        ValueError: If there is an issue with markdown syntax in the paragraph.
    """
    return tf.text_line_to_text_nodes(text=text)


def markdown_to_html_node(text: str) -> ParentNode:
    """
    Convert Markdown text to a ParentNode object representing the HTML structure.

    This function processes the input Markdown text, converting it into a hierarchical structure of HTML nodes.
    It splits the Markdown text into blocks, determines the type of each block, and converts each block to the
    corresponding HTML representation.

    Args:
        text (str): The Markdown text to be converted.

    Returns:
        ParentNode: A ParentNode object representing the HTML structure of the input Markdown text.
    """

    if not text:
        raise ValueError("Empty markdown input")

    nodes = list()
    markdown_blocks = markdown_to_blocks(text=text)
    markdown_block_types = [get_markdown_block_type(block) for block in markdown_blocks]

    for ix, block in enumerate(markdown_blocks):
        if markdown_block_types[ix] == BLOCK_TYPE_PARAGRAPH:
            nodes.append(
                ParentNode(
                    children=[
                        tf.text_node_to_html_node(node)
                        for node in markdown_paragraph_to_text_node(text=block)
                    ],
                    tag="p",
                )
            )
        elif markdown_block_types[ix] == BLOCK_TYPE_HEADING:
            nodes.append(
                ParentNode(
                    children=[
                        tf.text_node_to_html_node(node)
                        for node in markdown_heading_to_text_node(text=block)
                    ],
                    tag="h{}".format(block.count("#")),
                )
            )
        elif markdown_block_types[ix] == BLOCK_TYPE_CODE:
            # dedicated function not needed as we want to reserve the raw text
            # within the code blocks
            nodes.append(LeafNode(value=block[3:-3], tag="pre"))
        elif markdown_block_types[ix] == BLOCK_TYPE_QUOTE:
            nodes.append(
                ParentNode(
                    children=[
                        tf.text_node_to_html_node(node)
                        for node in markdown_quote_to_text_node(text=block)
                    ],
                    tag="blockquote",
                )
            )
        elif markdown_block_types[ix] == BLOCK_TYPE_UNORD_LIST:
            nodes.append(
                ParentNode(
                    children=[
                        ParentNode(
                            children=[
                                tf.text_node_to_html_node(node) for node in nodes
                            ],
                            tag="li",
                        )
                        for nodes in markdown_unord_list_to_text_node(text=block)
                    ],
                    tag="ul",
                )
            )
        elif markdown_block_types[ix] == BLOCK_TYPE_ORD_LIST:
            nodes.append(
                ParentNode(
                    children=[
                        ParentNode(
                            children=[
                                tf.text_node_to_html_node(node) for node in nodes
                            ],
                            tag="li",
                        )
                        for nodes in markdown_ord_list_to_text_node(text=block)
                    ],
                    tag="ol",
                )
            )

    return ParentNode(children=nodes, tag="div")
