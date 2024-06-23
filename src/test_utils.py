import unittest

from htmlnode import LeafNode
from textnode import TextNode
from utils import (
    TEXT_TYPE_BOLD,
    TEXT_TYPE_CODE,
    TEXT_TYPE_IMAGE,
    TEXT_TYPE_ITALIC,
    TEXT_TYPE_LINK,
    TEXT_TYPE_TEXT,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    text_node_to_html_node,
)


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text_type_text(self):
        text_node = TextNode(text="Hello", text_type=TEXT_TYPE_TEXT)
        leaf_node = text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "Hello")

    def test_text_type_bold(self):
        text_node = TextNode(text="Bold", text_type=TEXT_TYPE_BOLD)
        leaf_node = text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "<b>Bold</b>")

    def test_text_type_italic(self):
        text_node = TextNode(text="Italic", text_type=TEXT_TYPE_ITALIC)
        leaf_node = text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "<i>Italic</i>")

    def test_text_type_code(self):
        text_node = TextNode(text="Code", text_type=TEXT_TYPE_CODE)
        leaf_node = text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "<code>Code</code>")

    def test_text_type_link(self):
        text_node = TextNode(
            text="Link", text_type=TEXT_TYPE_LINK, url="http://example.com"
        )
        leaf_node = text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), '<a href="http://example.com">Link</a>')

    def test_text_type_image(self):
        text_node = TextNode(
            text="Image", text_type=TEXT_TYPE_IMAGE, url="http://example.com/image.jpg"
        )
        leaf_node = text_node_to_html_node(text_node)
        self.assertEqual(
            leaf_node.to_html(),
            '<img src="http://example.com/image.jpg" alt="Image" />',
        )

    def test_invalid_text_type(self):
        text_node = TextNode(text="Invalid", text_type="invalid")
        with self.assertRaises(ValueError):
            text_node_to_html_node(text_node)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_without_delimiter(self):
        nodes = [TextNode(text="Hello World", text_type=TEXT_TYPE_TEXT)]
        self.assertEqual(split_nodes_delimiter(nodes, "`", TEXT_TYPE_CODE), nodes)

    def test_split_nodes_with_delimiter(self):
        nodes = [TextNode(text="Hello `code` World", text_type=TEXT_TYPE_TEXT)]
        expected_nodes = [
            TextNode(text="Hello ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="code", text_type=TEXT_TYPE_CODE),
            TextNode(text=" World", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            split_nodes_delimiter(nodes, "`", TEXT_TYPE_CODE), expected_nodes
        )

    def test_split_nodes_with_multiple_delimiters(self):
        nodes = [
            TextNode(
                text="Hello `code` and `more code` World", text_type=TEXT_TYPE_TEXT
            )
        ]
        expected_nodes = [
            TextNode(text="Hello ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="code", text_type=TEXT_TYPE_CODE),
            TextNode(text=" and ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="more code", text_type=TEXT_TYPE_CODE),
            TextNode(text=" World", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            split_nodes_delimiter(nodes, "`", TEXT_TYPE_CODE), expected_nodes
        )

    def test_split_nodes_with_nested_delimiters(self):
        nodes = [
            TextNode(
                text="Hello `code with ``nested`` syntax` World",
                text_type=TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode(text="Hello ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="code with ", text_type=TEXT_TYPE_CODE),
            TextNode(text="nested", text_type=TEXT_TYPE_CODE),
            TextNode(text=" syntax", text_type=TEXT_TYPE_CODE),
            TextNode(text=" World", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            split_nodes_delimiter(nodes, "`", TEXT_TYPE_CODE), expected_nodes
        )

    def test_split_nodes_with_nested_delimiters_and_not_implemented(self):
        nodes = [
            TextNode(
                text="Another **test**.",
                text_type=TEXT_TYPE_TEXT,
            )
        ]
        with self.assertRaises(NotImplementedError):
            split_nodes_delimiter(nodes, "*", TEXT_TYPE_ITALIC)

    def test_split_nodes_with_nested_bold_delimiters(self):
        nodes = [
            TextNode(
                text="This is an *italic and **bold** word*.",
                text_type=TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode(text="This is an *italic and ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="bold", text_type=TEXT_TYPE_BOLD),
            TextNode(text=" word*.", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            split_nodes_delimiter(nodes, "**", TEXT_TYPE_BOLD), expected_nodes
        )

    def test_invalid_markdown_syntax(self):
        nodes = [TextNode(text="Hello `code World", text_type=TEXT_TYPE_TEXT)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "`", TEXT_TYPE_CODE)


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images_single(self):
        text = "This is an image ![alt text](http://example.com/image.jpg)."
        expected = [("alt text", "http://example.com/image.jpg")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_multiple(self):
        text = "This is an image ![alt text](http://example.com/image.jpg). Here is another ![another image](https://example.org/pic.png)."
        expected = [
            ("alt text", "http://example.com/image.jpg"),
            ("another image", "https://example.org/pic.png"),
        ]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_none(self):
        text = "No images here!"
        expected = []
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_broken(self):
        text = "Broken ![alt text(http://example.com/image.jpg)."
        expected = []
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_links_single(self):
        text = "This is a [link](http://example.com)."
        expected = [("link", "http://example.com")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_markdown_links_multiple(self):
        text = "This is a [link](http://example.com). Here is another [another link](https://example.org)."
        expected = [
            ("link", "http://example.com"),
            ("another link", "https://example.org"),
        ]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_markdown_links_none(self):
        text = "No links here!"
        expected = []
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_markdown_links_broken(self):
        text = "Broken [link(http://example.com)."
        expected = []
        self.assertEqual(extract_markdown_links(text), expected)


if __name__ == "__main__":
    unittest.main()
