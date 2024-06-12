from typing import List, Dict, TypeVar, Optional, Iterator

T = TypeVar("T")


class HTMLNode:
    """
    Base class for HTML nodes.

    Attributes:
        tag (Optional[str]): The tag name of the HTML element.
        value (Optional[str]): The text value of the HTML element.
        children (Optional[List["HTMLNode"]]): The list of child HTML nodes.
        props (Optional[Dict[str, str]]): The dictionary of HTML attributes.

    Raises:
        ValueError: If tag is not a string, value is not a string, children is not a list, a child in children is not an instance of HTMLNode, or props is not a dictionary.
    """

    def __init__(
        self,
        tag: Optional[str] = None,
        value: Optional[str] = None,
        children: Optional[List["HTMLNode"]] = None,
        props: Optional[Dict[str, str]] = None,
    ) -> None:
        if tag is not None and not isinstance(tag, str):
            raise ValueError("Node tag should be string")
        if value is not None and not isinstance(value, str):
            raise ValueError("Node value should be string")
        if children is not None and not isinstance(children, List):
            raise ValueError("Node children must be a list")
        if children is not None and len(children) > 0:
            for child in children:
                if not isinstance(child, HTMLNode):
                    raise ValueError(
                        "Node children must be a HTMLNode class\
                                     object"
                    )
        if props is not None and not isinstance(props, dict):
            raise ValueError("Node Properties should be dictionary")
        self.tag = tag
        self.value = value
        self.children = children if children is not None else []
        self.props = props if props is not None else {}

    def to_html(self) -> None:
        """
        Convert the HTMLNode to its HTML representation.

        This method should be implemented by subclasses.

        Returns:
            str: The HTML representation of the HTMLNode.

        Raises:
            NotImplementedError: This method is meant to be implemented by subclasses.
        """
        raise NotImplementedError()

    def props_to_html(self) -> str:
        """
        Convert the props dictionary to HTML attribute string.

        Returns:
            str: The HTML attribute string.
        """
        html = ""
        if self.props:
            for prop, value in self.props.items():
                html += '{}="{}" '.format(prop, value)
        return html.rstrip()

    def __repr__(self, indent: int = 0) -> str:
        """
        Return a string representation of the HTMLNode.

        Args:
            indent (int): The number of spaces for indentation.

        Returns:
            str: The string representation of the HTMLNode.
        """
        indent_str = " " * indent
        if self.children:
            children_repr = ",\n".join(
                child.__repr__(indent + 4) for child in self.children
            )
        else:
            children_repr = "None"
        props_repr = ", ".join(f'"{k}": "{v}"' for k, v in self.props.items())
        return (
            f"{indent_str}HTMLNode(\n"
            f"{indent_str}  Tag: {self.tag},\n"
            f"{indent_str}  Value: {self.value},\n"
            f"{indent_str}  Children: [\n{children_repr}\n{indent_str}  ],\n"
            f"{indent_str}  Props: {{ {props_repr} }}\n"
            f"{indent_str})"
        )

    def __iter__(self) -> Iterator[T]:
        """
        Return an iterator over the children of the HTMLNode.

        Returns:
            Iterator[T]: An iterator over the children.
        """
        return iter(self.children)


class LeafNode(HTMLNode):
    """
    Represents a leaf node in an HTML tree.

    Attributes:
        value (str): The text value of the HTML element.
        tag (Optional[str]): The tag name of the HTML element.
        props (Optional[Dict[str, str]]): The dictionary of HTML attributes.

    Raises:
        ValueError: If the tag is missing and the value is not provided, or if the value is an empty string.
    """

    def __init__(
        self,
        value: str,
        tag: Optional[str] = None,
        props: Optional[Dict[str, str]] = None,
    ) -> None:
        if value is None:
            raise ValueError("Value must be provided for LeafNode")
        super().__init__(tag, value, None, props)

    def to_html(self) -> str:
        """
        Convert the LeafNode to its HTML representation.

        Returns:
            str: The HTML representation of the LeafNode.
        """
        if not self.tag:
            return self.value
        elif not self.props:
            return "<{}>{}</{}>".format(self.tag, self.value, self.tag)
        elif self.tag and self.props:
            if self.tag == "img":
                return "<{} {}{} />".format(self.tag, self.props_to_html(), self.value)
            else:
                return "<{} {}>{}</{}>".format(
                    self.tag, self.props_to_html(), self.value, self.tag
                )


class ParentNode(HTMLNode):
    """
    Initialize a ParentNode instance.

    Args:
        children (Optional[List["HTMLNode"]]): The list of child HTML nodes.
        tag (Optional[str]): The tag name of the HTML element.
        props (Optional[Dict[str, str]]): The dictionary of HTML attributes.

    Raises:
        ValueError: If the tag is missing or if children nodes are not provided.
    """

    def __init__(
        self,
        children: Optional[List["HTMLNode"]],
        tag: Optional[str] = None,
        props: Optional[Dict[str, str]] = None,
    ) -> None:
        if not tag:
            raise ValueError("Tag must be provided for ParentNode")
        elif not children or not len(children) > 0:
            raise ValueError("Children nodes must be provided for ParentNode")
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        """
        Convert the ParentNode to its HTML representation.

        Returns:
            str: The HTML representation of the ParentNode.
        """
        if self.tag is None:
            raise ValueError("Tag must be provided for ParentNode")
        html_string = "<{}".format(self.tag)
        if self.props:
            html_string += " {}>".format(self.props_to_html())
        else:
            html_string += ">"
        for child in self.children:
            html_string += child.to_html()
        html_string += "</{}>".format(self.tag)
        return html_string
