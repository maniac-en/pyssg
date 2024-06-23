import unittest

from src.core.htmlnode import LeafNode
from src.core.textnode import TextNode
from src.core.utils import *


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


class TestExtractMarkdownImageLink(unittest.TestCase):
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


class TestSplitNodeImage(unittest.TestCase):
    def test_split_node_image_single(self):
        nodes = [
            TextNode(
                "This is text with an ![image](https://example.com/image.jpg)",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is text with an ", TEXT_TYPE_TEXT),
            TextNode(
                "image",
                TEXT_TYPE_IMAGE,
                "https://example.com/image.jpg",
            ),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_node_image_multiple(self):
        nodes = [
            TextNode(
                "This is an image ![alt text](http://example.com/image.jpg). Here is another ![another image](https://example.org/pic.png).",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is an image ", TEXT_TYPE_TEXT),
            TextNode(
                "alt text",
                TEXT_TYPE_IMAGE,
                "http://example.com/image.jpg",
            ),
            TextNode(". Here is another ", TEXT_TYPE_TEXT),
            TextNode(
                "another image",
                TEXT_TYPE_IMAGE,
                "https://example.org/pic.png",
            ),
            TextNode(".", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_node_image_none(self):
        nodes = [
            TextNode(
                "This is text without any images.",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is text without any images.", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_node_image_non_text_type(self):
        nodes = [TextNode("This should not be split", TEXT_TYPE_BOLD)]
        expected_nodes = [TextNode("This should not be split", TEXT_TYPE_BOLD)]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_node_image_text_type(self):
        nodes = [
            TextNode(
                "This is an image ![alt text](http://example.com/image.jpg).",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is an image ", TEXT_TYPE_TEXT),
            TextNode("alt text", TEXT_TYPE_IMAGE, "http://example.com/image.jpg"),
            TextNode(".", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_node_image_broken(self):
        nodes = [
            TextNode(
                "This is an image with a broken ![alt text](http://example.com/image.jpg link.",
                TEXT_TYPE_TEXT,
            )
        ]
        with self.assertRaises(ValueError):
            split_nodes_image(nodes)


class TestSplitNodeLink(unittest.TestCase):
    def test_split_node_link_single(self):
        nodes = [
            TextNode(
                "This is a [link](https://example.com)",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is a ", TEXT_TYPE_TEXT),
            TextNode(
                "link",
                TEXT_TYPE_LINK,
                "https://example.com",
            ),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_node_link_multiple(self):
        nodes = [
            TextNode(
                "This is a [link](http://example.com). Here is another [another link](https://example.org).",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is a ", TEXT_TYPE_TEXT),
            TextNode(
                "link",
                TEXT_TYPE_LINK,
                "http://example.com",
            ),
            TextNode(". Here is another ", TEXT_TYPE_TEXT),
            TextNode(
                "another link",
                TEXT_TYPE_LINK,
                "https://example.org",
            ),
            TextNode(".", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_node_link_none(self):
        nodes = [
            TextNode(
                "This is text without any links.",
                TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is text without any links.", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_node_link_non_text_type(self):
        nodes = [TextNode("This should not be split", TEXT_TYPE_BOLD)]
        expected_nodes = [TextNode("This should not be split", TEXT_TYPE_BOLD)]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_node_link_text_type(self):
        nodes = [TextNode("This is a [link](http://example.com).", TEXT_TYPE_TEXT)]
        expected_nodes = [
            TextNode("This is a ", TEXT_TYPE_TEXT),
            TextNode("link", TEXT_TYPE_LINK, "http://example.com"),
            TextNode(".", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_node_link_broken(self):
        nodes = [
            TextNode(
                "This is a [link](http://example.com text with a broken link.",
                TEXT_TYPE_TEXT,
            )
        ]
        with self.assertRaises(ValueError):
            split_nodes_link(nodes)


class TestConvertMarkdownToNodes(unittest.TestCase):
    def test_convert_markdown_to_nodes_basic(self):
        text = """This is **text** with an *italic* word and a `code block` and an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and a [link](https://boot.dev)"""
        expected_nodes = [
            TextNode("This is ", TEXT_TYPE_TEXT),
            TextNode("text", TEXT_TYPE_BOLD),
            TextNode(" with an ", TEXT_TYPE_TEXT),
            TextNode("italic", TEXT_TYPE_ITALIC),
            TextNode(" word and a ", TEXT_TYPE_TEXT),
            TextNode("code block", TEXT_TYPE_CODE),
            TextNode(" and an ", TEXT_TYPE_TEXT),
            TextNode(
                "image",
                TEXT_TYPE_IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and a ", TEXT_TYPE_TEXT),
            TextNode("link", TEXT_TYPE_LINK, "https://boot.dev"),
        ]
        self.assertEqual(convert_inline_markdown_to_nodes(text), expected_nodes)

    def test_convert_markdown_to_nodes_invalid_markdown(self):
        text = "This is a [broken link](http://example.com."
        with self.assertRaises(ValueError):
            convert_inline_markdown_to_nodes(text)


if __name__ == "__main__":
    unittest.main()
