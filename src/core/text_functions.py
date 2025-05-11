from typing import List
from src.core.htmlnode import LeafNode
from src.core.textnode import TextNode
import src.core.markdown_functions as mf

TEXT_TYPE_TEXT = "text"
TEXT_TYPE_BOLD = "bold"
TEXT_TYPE_ITALIC = "italic"
TEXT_TYPE_CODE = "code"
TEXT_TYPE_LINK = "link"
TEXT_TYPE_IMAGE = "image"


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
        >>> nodes = [TextNode("This is _italic_ and **bold** text", TEXT_TYPE_TEXT)]
        >>> result = split_nodes_delimiter(nodes, "_", TEXT_TYPE_ITALIC)
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


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    """
    Split nodes containing markdown images into separate text and image nodes.

    Args:
        old_nodes (List[TextNode]): A list of nodes to be split.

    Returns:
        List[TextNode]: A list of TextNode objects including new TextNode objects if necessary.

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
    for node in old_nodes:
        if not isinstance(node, TextNode):
            resultant_nodes.append(node)
        elif node.text_type != TEXT_TYPE_TEXT:
            resultant_nodes.append(node)
        else:
            current_text = node.text
            while True:
                if current_text and "!" not in current_text:
                    resultant_nodes.append(
                        TextNode(text=current_text, text_type=TEXT_TYPE_TEXT)
                    )
                    break

                # broken images, or, text with exclamation mark
                # so if no images found, assume the text as TEXT_TYPE_TEXT
                # and append to resultant_nodes
                images = mf.extract_markdown_images(text=current_text)
                if not images:
                    resultant_nodes.append(
                        TextNode(text=current_text, text_type=TEXT_TYPE_TEXT)
                    )
                    break

                # first image tuple
                image_tuple = mf.extract_markdown_images(text=current_text)[0]

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
    for node in old_nodes:
        if not isinstance(node, TextNode):
            resultant_nodes.append(node)
        elif node.text_type != TEXT_TYPE_TEXT:
            resultant_nodes.append(node)
        else:
            current_text = node.text
            while True:
                if current_text and "[" not in current_text:
                    resultant_nodes.append(
                        TextNode(text=current_text, text_type=TEXT_TYPE_TEXT)
                    )
                    break

                # first link tuple
                try:
                    link_tuple = mf.extract_markdown_links(text=current_text)[0]
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


def text_line_to_text_nodes(text: str) -> List[TextNode]:
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
        text_nodes = split_nodes_delimiter(text_nodes, "_", TEXT_TYPE_ITALIC)
        text_nodes = split_nodes_delimiter(text_nodes, "`", TEXT_TYPE_CODE)
    except ValueError as e:
        raise e

    return text_nodes
