from typing import Optional

from htmlnode import LeafNode


class TextNode:
    """
    Initialize a TextNode object.

    Args:
        text (str): The text content of the node.
        text_type (str): The type of text content, e.g., 'plain', 'markdown', etc.
        url (Optional[str]): The URL associated with the text (default is None).

    Raises:
        ValueError: If text is not provided or is not a string, or, text_type is not provided or is not a string, or, URL is not a string.
    """

    def __init__(self, text: str, text_type: str, url: Optional[str] = None) -> None:
        if not text:
            raise ValueError("Text must be provided for TextNode")
        if not isinstance(text, str):
            raise ValueError("Text for TextNode must be a string")
        if not text_type:
            raise ValueError("Text type must be provided for TextNode")
        if not isinstance(text_type, str):
            raise ValueError("Text type for TextNode must be a string")
        if url is not None and not isinstance(url, str):
            raise ValueError("URl for TextNode must be a string")

        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other) -> bool:
        """
        Compare two TextNode objects for equality.

        Two TextNode objects are considered equal if they have the same text, text_type, and URL.

        Args:
            other (TextNode): The other TextNode object to compare against.

        Returns:
            bool: True if the two TextNode objects are equal, False otherwise.
        """
        if (
            isinstance(other, TextNode)
            and self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        ):
            return True
        return False

    def __repr__(self) -> str:
        """
        Return a string representation of the TextNode object.

        Returns:
            str: A string representation of the TextNode object.
        """
        return 'TextNode("{}", {}, {})'.format(self.text, self.text_type, self.url)
