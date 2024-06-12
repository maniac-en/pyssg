from htmlnode import LeafNode
from textnode import TextNode

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


def split_nodes_delimiter(old_nodes: list, delimiter: str, text_type: str) -> list:
    """
    Split a list of nodes based on a delimiter in their text content.

    Args:
        old_nodes (list): A list of nodes to be split.
        delimiter (str): The delimiter to split the nodes on.
        text_type (str): The text type to assign to new TextNode objects.

    Returns:
        list: A list of nodes after splitting, including new TextNode objects if necessary.

    Raises:
        ValueError: If the markdown syntax in any node is invalid.
        NotImplementedError: If the delimiter is nested within a node's text.
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

        # pending part after all delimited words, or,
        # if there's no delimiter in entire text
        if current_part[:-delimiter_length]:
            parts.append(current_part)

        return parts

    for node in old_nodes:
        if not isinstance(node, TextNode):
            delimited_nodes.append(node)
        if node.text.count(delimiter) % 2 != 0:
            raise ValueError("Invalid markdown syntax")
        parts = extract_parts(node.text)
        if parts[0] == node.text:
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
