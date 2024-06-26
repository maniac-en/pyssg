import re
from typing import List, Tuple
from src.core.htmlnode import HTMLNode, LeafNode, ParentNode
from src.core.textnode import TextNode

TEXT_TYPE_TEXT = "text"
TEXT_TYPE_BOLD = "bold"
TEXT_TYPE_ITALIC = "italic"
TEXT_TYPE_CODE = "code"
TEXT_TYPE_LINK = "link"
TEXT_TYPE_IMAGE = "image"
BLOCK_TYPE_PARAGRAPH = "paragraph"
BLOCK_TYPE_HEADING = "heading"
BLOCK_TYPE_CODE = "code"
BLOCK_TYPE_QUOTE = "quote"
BLOCK_TYPE_UNORD_LIST = "unordered_list"
BLOCK_TYPE_ORD_LIST = "ordered_list"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    """
    Convert a TextNode object to a LeafNode object for HTML representation.

    Args:
        text_node (TextNode): The TextNode object to convert.

    Returns:
        LeafNode: The corresponding LeafNode object for HTML representation.

    Raises:
        ValueError: If the text_node has an invalid text_type.
    """
    if text_node.text_type == TEXT_TYPE_TEXT:
        return LeafNode(value=text_node.text)
    elif text_node.text_type == TEXT_TYPE_BOLD:
        return LeafNode(value=text_node.text, tag="b")
    elif text_node.text_type == TEXT_TYPE_ITALIC:
        return LeafNode(value=text_node.text, tag="i")
    elif text_node.text_type == TEXT_TYPE_CODE:
        return LeafNode(value=text_node.text, tag="code")
    elif text_node.text_type == TEXT_TYPE_LINK:
        return LeafNode(value=text_node.text, tag="a", props={"href": text_node.url})
    elif text_node.text_type == TEXT_TYPE_IMAGE:
        return LeafNode(
            value="", tag="img", props={"src": text_node.url, "alt": text_node.text}
        )
    else:
        raise ValueError(
            "Text Node has invalid type:\
            {}".format(text_node.text_type)
        )


def split_nodes_delimiter(
    old_nodes: List[TextNode], delimiter: str, text_type: str
) -> List[TextNode]:
    """
    Split a list of TextNode objects based on a delimiter in their text content.

    Args:
        old_nodes (List[TextNode]): A list of TextNode objects to be split.
        delimiter (str): The delimiter to split the nodes on.
        text_type (str): The text type to assign to new TextNode objects.

    Returns:
        List[TextNode]: A list of TextNode objects after splitting, including new TextNode objects if necessary.

    Raises:
        ValueError: If the markdown syntax in any node is invalid.
        NotImplementedError: If the delimiter is nested within a node's text.

    Example:
        >>> nodes = [TextNode("This is *italic* and **bold** text", TEXT_TYPE_TEXT)]
        >>> result = split_nodes_delimiter(nodes, "*", TEXT_TYPE_ITALIC)
        >>> for node in result:
        >>>     print(f"text: {node.text}, type: {node.text_type}")
        text: This is , type: TEXT_TYPE_TEXT
        text: italic, type: TEXT_TYPE_ITALIC
        text:  and **bold** text, type: TEXT_TYPE_TEXT
    """
    delimited_nodes = list()

    def extract_parts(text: str) -> list:
        nonlocal delimiter
        parts = list()

        current_part = ""
        delim_found = False
        delimiter_length = len(delimiter)

        for char in text:
            current_part += char
            if current_part.endswith(delimiter):
                if delim_found:
                    if not current_part[delimiter_length:-delimiter_length]:
                        continue
                    if current_part.count(delimiter) % 2 != 0:
                        raise NotImplementedError()

                    # delimited word finished
                    parts.append(current_part)
                    current_part = ""
                    delim_found = False
                    continue
                else:
                    # non-delimited word finished
                    if current_part[:-delimiter_length]:
                        parts.append(current_part[:-delimiter_length])
                    current_part = delimiter  # starting new delimited part
                    delim_found = True
                    continue

        # pending part after all delimited words
        if current_part:
            parts.append(current_part)

        return parts

    for node in old_nodes:
        if not isinstance(node, TextNode) or delimiter not in node.text:
            delimited_nodes.append(node)
            continue
        if node.text.count(delimiter) % 2 != 0:
            raise ValueError("Invalid markdown syntax")

        # extract parts based on delimiter
        parts = extract_parts(node.text)

        # not parts[0].startswith(delimiter) is needed when the node text only
        # has a delimited word
        if parts[0] == node.text and not parts[0].startswith(delimiter):
            delimited_nodes.append(node)
            continue
        else:
            for part in parts:
                if part.startswith(delimiter):
                    delimited_nodes.append(
                        TextNode(part[len(delimiter) : -len(delimiter)], text_type)
                    )
                else:
                    delimited_nodes.append(TextNode(part, TEXT_TYPE_TEXT))

    return delimited_nodes


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


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    """
    Split nodes containing markdown images into separate text and image nodes.

    Args:
        old_nodes (List[TextNode]): A list of nodes to be split.

    Returns:
        List[TextNode]: A list of TextNode objects including new TextNode objects if necessary.

    Raises:
        ValueError: If there is an issue with markdown syntax.

    The function processes each node to check if it is an instance of TextNode with text type TEXT_TYPE_TEXT.
    If it contains markdown images, it splits the text around the images and creates new TextNode objects for
    each text and image segment.

    Example:
        >>> nodes = [TextNode("This is text with an ![image](http://example.com/image.jpg)", TEXT_TYPE_TEXT)]
        >>> split_nodes_image(nodes)
        [TextNode("This is text with an ", TEXT_TYPE_TEXT), TextNode("image", TEXT_TYPE_IMAGE, "http://example.com/image.jpg")]

        >>> nodes = [TextNode("Here is ![first](http://example.com/1.jpg) and ![second](http://example.com/2.jpg) images", TEXT_TYPE_TEXT)]
        >>> split_nodes_image(nodes)
        [TextNode("Here is ", TEXT_TYPE_TEXT), TextNode("first", TEXT_TYPE_IMAGE, "http://example.com/1.jpg"),
         TextNode(" and ", TEXT_TYPE_TEXT), TextNode("second", TEXT_TYPE_IMAGE, "http://example.com/2.jpg"),
         TextNode(" images", TEXT_TYPE_TEXT)]
    """
    resultant_nodes = list()
    delimiter = "!"
    for node in old_nodes:
        if not isinstance(node, TextNode):
            resultant_nodes.append(node)
        elif node.text_type != TEXT_TYPE_TEXT:
            resultant_nodes.append(node)
        else:
            current_text = node.text
            while True:
                if current_text and delimiter not in current_text:
                    resultant_nodes.append(
                        TextNode(text=current_text, text_type=TEXT_TYPE_TEXT)
                    )
                    break

                # first image tuple
                try:
                    image_tuple = extract_markdown_images(text=current_text)[0]
                except IndexError:
                    raise ValueError("Invalid markdown")

                splits = current_text.split(
                    f"![{image_tuple[0]}]({image_tuple[1]})", maxsplit=1
                )

                if splits[0]:
                    resultant_nodes.append(
                        TextNode(text=splits[0], text_type=TEXT_TYPE_TEXT)
                    )

                resultant_nodes.append(
                    TextNode(
                        text=image_tuple[0],
                        text_type=TEXT_TYPE_IMAGE,
                        url=image_tuple[1],
                    )
                )

                if splits[1]:
                    current_text = splits[1]
                    continue
                break

    return resultant_nodes


def split_nodes_link(old_nodes: List[TextNode]) -> List[TextNode]:
    """
    Split nodes containing markdown links into separate text and link nodes.

    Args:
        old_nodes (List[TextNode]): A list of nodes to be split.

    Returns:
        List[TextNode]: A list of TextNode objects including new TextNode objects if necessary.

    Raises:
        ValueError: If there is an issue with markdown syntax.

    The function processes each node to check if it is an instance of TextNode with text type TEXT_TYPE_TEXT.
    If it contains markdown links, it splits the text around the links and creates new TextNode objects for
    each text and link segment.

    Example:
        >>> nodes = [TextNode("This is a [link](http://example.com)", TEXT_TYPE_TEXT)]
        >>> split_nodes_link(nodes)
        [TextNode("This is a ", TEXT_TYPE_TEXT), TextNode("link", TEXT_TYPE_LINK, "http://example.com")]

        >>> nodes = [TextNode("Here is [first](http://example.com/1) and [second](http://example.com/2) links", TEXT_TYPE_TEXT)]
        >>> split_nodes_link(nodes)
        [TextNode("Here is ", TEXT_TYPE_TEXT), TextNode("first", TEXT_TYPE_LINK, "http://example.com/1"),
         TextNode(" and ", TEXT_TYPE_TEXT), TextNode("second", TEXT_TYPE_LINK, "http://example.com/2"),
         TextNode(" links", TEXT_TYPE_TEXT)]
    """
    resultant_nodes = list()
    delimiter = " ["
    for node in old_nodes:
        if not isinstance(node, TextNode):
            resultant_nodes.append(node)
        elif node.text_type != TEXT_TYPE_TEXT:
            resultant_nodes.append(node)
        else:
            current_text = node.text
            while True:
                if current_text and delimiter not in current_text:
                    resultant_nodes.append(
                        TextNode(text=current_text, text_type=TEXT_TYPE_TEXT)
                    )
                    break

                # first link tuple
                try:
                    link_tuple = extract_markdown_links(text=current_text)[0]
                except IndexError:
                    raise ValueError("Invalid markdown")

                splits = current_text.split(
                    f"[{link_tuple[0]}]({link_tuple[1]})", maxsplit=1
                )

                if splits[0]:
                    resultant_nodes.append(
                        TextNode(text=splits[0], text_type=TEXT_TYPE_TEXT)
                    )

                resultant_nodes.append(
                    TextNode(
                        text=link_tuple[0],
                        text_type=TEXT_TYPE_LINK,
                        url=link_tuple[1],
                    )
                )

                if splits[1]:
                    current_text = splits[1]
                    continue
                break

    return resultant_nodes


def markdown_line_to_nodes(text: str) -> List[TextNode]:
    """
    Convert Markdown text to a list of TextNode objects.

    Args:
        markdown_text (str): The Markdown text to convert.

    Returns:
        List[TextNode]: A list of TextNode objects representing the Markdown text.

    Raises:
        ValueError: If there is an issue with markdown syntax.
    """
    text_nodes = [TextNode(text=text, text_type=TEXT_TYPE_TEXT)]

    try:
        text_nodes = split_nodes_image(text_nodes)
        text_nodes = split_nodes_link(text_nodes)
        text_nodes = split_nodes_delimiter(text_nodes, "**", TEXT_TYPE_BOLD)
        text_nodes = split_nodes_delimiter(text_nodes, "*", TEXT_TYPE_ITALIC)
        text_nodes = split_nodes_delimiter(text_nodes, "`", TEXT_TYPE_CODE)
    except ValueError as e:
        raise e

    return text_nodes


def markdown_to_blocks(text: str) -> List[str]:
    """
    Convert a raw Markdown string into a list of block strings.

    This function splits the input Markdown string into distinct blocks, where each
    block is separated by one or more newlines. It strips any leading or trailing
    whitespace from each block and removes any empty blocks created by excessive newlines.

    Parameters:
    text (str): The raw Markdown string representing a full document.

    Returns:
    List[str]: A list of block strings, with leading and trailing whitespace removed.
    """
    lines = text.split("\n")
    blocks = []
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


def get_block_type(block: str) -> str:
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
        return markdown_line_to_nodes(text=text.replace("#", "").lstrip())
    else:
        return markdown_line_to_nodes(text=text)


def markdown_quote_to_text_node(text: str) -> List[TextNode]:
    pass  # Yet to be implemented


def markdown_unord_list_to_text_node(text: str) -> List[TextNode]:
    pass  # Yet to be implemented


def markdown_ord_list_to_text_node(text: str) -> List[TextNode]:
    pass  # Yet to be implemented


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
    return markdown_line_to_nodes(text=text)


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
    nodes = list()
    markdown_blocks = markdown_to_blocks(text=text)
    markdown_block_types = [get_block_type(block) for block in markdown_blocks]

    for ix, block in enumerate(markdown_blocks):
        if markdown_block_types[ix] == BLOCK_TYPE_PARAGRAPH:
            nodes.append(
                ParentNode(
                    children=[
                        text_node_to_html_node(node)
                        for node in markdown_paragraph_to_text_node(text=block)
                    ],
                    tag="p",
                )
            )
        elif markdown_block_types[ix] == BLOCK_TYPE_HEADING:
            nodes.append(
                ParentNode(
                    children=[
                        text_node_to_html_node(node)
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
            nodes.append()  # Yet to be implemented
        elif markdown_block_types[ix] == BLOCK_TYPE_ORD_LIST:
            nodes.append()  # Yet to be implemented
        elif markdown_block_types[ix] == BLOCK_TYPE_UNORD_LIST:
            nodes.append()  # Yet to be implemented

    return ParentNode(children=nodes, tag="div")
