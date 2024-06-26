import unittest

# import sys
# import os
#
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/.." + "/../")

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

    def test_split_nodes_with_only_delimited_word(self):
        nodes = [TextNode(text="*italic word*", text_type=TEXT_TYPE_TEXT)]
        expected_nodes = [TextNode(text="italic word", text_type=TEXT_TYPE_ITALIC)]
        self.assertEqual(
            split_nodes_delimiter(nodes, "*", TEXT_TYPE_ITALIC), expected_nodes
        )

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


class TestMarkdownLineToNodes(unittest.TestCase):
    def test_markdown_line_to_node_plain_text(self):
        text = "This is a plain text."
        expected = [TextNode(text="This is a plain text.", text_type=TEXT_TYPE_TEXT)]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_bold_text(self):
        text = "This is **bold** text."
        expected = [
            TextNode(text="This is ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="bold", text_type=TEXT_TYPE_BOLD),
            TextNode(text=" text.", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_italic_text(self):
        text = "This is *italic* text."
        expected = [
            TextNode(text="This is ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="italic", text_type=TEXT_TYPE_ITALIC),
            TextNode(text=" text.", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_code_text(self):
        text = "This is `code` text."
        expected = [
            TextNode(text="This is ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="code", text_type=TEXT_TYPE_CODE),
            TextNode(text=" text.", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_image_text(self):
        text = "This is an ![image](http://example.com/image.jpg)."
        expected = [
            TextNode(text="This is an ", text_type=TEXT_TYPE_TEXT),
            TextNode(
                text="image",
                text_type=TEXT_TYPE_IMAGE,
                url="http://example.com/image.jpg",
            ),
            TextNode(text=".", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_link_text(self):
        text = "This is a [link](http://example.com)."
        expected = [
            TextNode(text="This is a ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="link", text_type=TEXT_TYPE_LINK, url="http://example.com"),
            TextNode(text=".", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_combined_markdown(self):
        text = "This is **bold** and *italic* with a [link](http://example.com) and an ![image](http://example.com/image.jpg)."
        expected = [
            TextNode(text="This is ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="bold", text_type=TEXT_TYPE_BOLD),
            TextNode(text=" and ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="italic", text_type=TEXT_TYPE_ITALIC),
            TextNode(text=" with a ", text_type=TEXT_TYPE_TEXT),
            TextNode(text="link", text_type=TEXT_TYPE_LINK, url="http://example.com"),
            TextNode(text=" and an ", text_type=TEXT_TYPE_TEXT),
            TextNode(
                text="image",
                text_type=TEXT_TYPE_IMAGE,
                url="http://example.com/image.jpg",
            ),
            TextNode(text=".", text_type=TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_line_to_nodes(text), expected)

    def test_markdown_line_to_node_invalid_syntax(self):
        text = "This is **invalid markdown*."
        with self.assertRaises(ValueError):
            markdown_line_to_nodes(text)


class TestConvertMarkdownToBlock(unittest.TestCase):
    def test_convert_markdown_to_block_single_paragraph(self):
        text = "This is a paragraph."
        expected = ["This is a paragraph."]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_convert_markdown_to_block_multiple_paragraphs(self):
        text = """
        This is a paragraph.

        This is another paragraph.
        """
        expected = ["This is a paragraph.", "This is another paragraph."]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_convert_markdown_to_block_list_items(self):
        text = """
        * Item 1
        * Item 2
        """
        expected = ["* Item 1\n* Item 2"]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_convert_markdown_to_block_mixed_content(self):
        text = """
        This is **bolded** paragraph

        This is another paragraph with *italic* text and `code` here
        This is the same paragraph on a new line

        * This is a list
        * with items

        1. This is also a list
        2. with items
        """
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
            "* This is a list\n* with items",
            "1. This is also a list\n2. with items",
        ]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_convert_markdown_to_block_empty_input(self):
        text = ""
        expected = []
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_convert_markdown_to_block_only_newlines(self):
        text = "\n\n\n"
        expected = []
        self.assertEqual(markdown_to_blocks(text), expected)


class TestBlockToBlockType(unittest.TestCase):
    def test_get_block_type_heading(self):
        self.assertEqual(get_block_type("# Heading"), BLOCK_TYPE_HEADING)
        self.assertEqual(get_block_type("## Subheading"), BLOCK_TYPE_HEADING)
        self.assertEqual(get_block_type("###### Small heading"), BLOCK_TYPE_HEADING)

    def test_get_block_type_code(self):
        self.assertEqual(get_block_type("```code block```"), BLOCK_TYPE_CODE)
        self.assertEqual(
            get_block_type("```\nprint('Hello, world!')\n```"), BLOCK_TYPE_CODE
        )

    def test_get_block_type_quote(self):
        self.assertEqual(get_block_type("> This is a quote"), BLOCK_TYPE_QUOTE)
        self.assertEqual(
            get_block_type("> This is a quote\n> with multiple lines"), BLOCK_TYPE_QUOTE
        )

    def test_get_block_type_unordered_list(self):
        self.assertEqual(get_block_type("* Unordered list item"), BLOCK_TYPE_UNORD_LIST)
        self.assertEqual(
            get_block_type("- Another unordered list item"), BLOCK_TYPE_UNORD_LIST
        )
        self.assertEqual(
            get_block_type("* List item\n* Another list item"), BLOCK_TYPE_UNORD_LIST
        )

    def test_get_block_type_ordered_list(self):
        self.assertEqual(get_block_type("1. Ordered list item"), BLOCK_TYPE_ORD_LIST)
        self.assertEqual(
            get_block_type("1. First item\n2. Second item\n3. Third item"),
            BLOCK_TYPE_ORD_LIST,
        )

    def test_get_block_type_paragraph(self):
        self.assertEqual(get_block_type("Just a paragraph."), BLOCK_TYPE_PARAGRAPH)
        self.assertEqual(
            get_block_type("This is a **bold** text."), BLOCK_TYPE_PARAGRAPH
        )
        self.assertEqual(get_block_type("#Heading without space"), BLOCK_TYPE_PARAGRAPH)

    def test_get_block_type_invalid_heading(self):
        self.assertEqual(
            get_block_type("####### Invalid heading"), BLOCK_TYPE_PARAGRAPH
        )

    def test_get_block_type_invalid_quote(self):
        self.assertEqual(
            get_block_type("> line 1\nline without >\n> line 2"), BLOCK_TYPE_PARAGRAPH
        )

    def test_get_block_type_invalid_unordered_list(self):
        self.assertEqual(
            get_block_type("* line 1\nline without *\n* line 2"), BLOCK_TYPE_PARAGRAPH
        )

    def test_get_block_type_invalid_ordered_list(self):
        self.assertEqual(get_block_type("1 Not an ordered list"), BLOCK_TYPE_PARAGRAPH)
        self.assertEqual(
            get_block_type("1. First item\n3. Third item"), BLOCK_TYPE_PARAGRAPH
        )


class TestMarkdownToTextNode(unittest.TestCase):
    def test_markdown_paragraph_to_text_node_single_line(self):
        text = "This is **bolded** paragraph"
        expected_nodes = [
            TextNode("This is ", TEXT_TYPE_TEXT),
            TextNode("bolded", TEXT_TYPE_BOLD),
            TextNode(" paragraph", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_paragraph_to_text_node(text=text), expected_nodes)

    def test_markdown_paragraph_to_text_node_multi_line(self):
        text = """\
This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line\
"""
        expected_nodes = [
            TextNode("This is another paragraph with ", TEXT_TYPE_TEXT),
            TextNode("italic", TEXT_TYPE_ITALIC),
            TextNode(" text and ", TEXT_TYPE_TEXT),
            TextNode("code", TEXT_TYPE_CODE),
            TextNode(" here\nThis is the same paragraph on a new line", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_paragraph_to_text_node(text=text), expected_nodes)

    def test_markdown_heading_to_text_node_plain_h1(self):
        text = "# heading1"
        expected_nodes = [TextNode("heading1", TEXT_TYPE_TEXT)]
        self.assertEqual(markdown_heading_to_text_node(text=text), expected_nodes)

    def test_markdown_heading_to_text_node_italic_h2(self):
        text = "## *heading2*"
        expected_nodes = [TextNode("heading2", TEXT_TYPE_ITALIC)]
        self.assertEqual(markdown_heading_to_text_node(text=text), expected_nodes)

    def test_markdown_heading_to_text_node_bold_h3(self):
        text = "### **heading3**"
        expected_nodes = [TextNode("heading3", TEXT_TYPE_BOLD)]
        self.assertEqual(markdown_heading_to_text_node(text=text), expected_nodes)

    def test_markdown_heading_to_text_node_mix_text_h4(self):
        text = "#### `heading4` with **bold** word"
        expected_nodes = [
            TextNode("heading4", TEXT_TYPE_CODE),
            TextNode(" with ", TEXT_TYPE_TEXT),
            TextNode("bold", TEXT_TYPE_BOLD),
            TextNode(" word", TEXT_TYPE_TEXT),
        ]
        self.assertEqual(markdown_heading_to_text_node(text=text), expected_nodes)

    def test_markdown_heading_to_text_node_invalid_heading(self):
        text = "####### heading7 doesn't exist"
        expected_nodes = [TextNode("####### heading7 doesn't exist", TEXT_TYPE_TEXT)]
        self.assertEqual(markdown_heading_to_text_node(text=text), expected_nodes)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_markdown_to_html_paragraph_single_line(self):
        text = "This is **bolded** paragraph"
        expected = ParentNode(
            children=[
                ParentNode(
                    [
                        LeafNode(value="This is "),
                        LeafNode(value="bolded", tag="b"),
                        LeafNode(value=" paragraph"),
                    ],
                    tag="p",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_paragraph_to_text_node_multi_line(self):
        text = """\
This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line\
"""
        expected = ParentNode(
            children=[
                ParentNode(
                    [
                        LeafNode(value="This is another paragraph with "),
                        LeafNode(value="italic", tag="i"),
                        LeafNode(value=" text and "),
                        LeafNode(value="code", tag="code"),
                        LeafNode(
                            value=" here\nThis is the same paragraph on a new line"
                        ),
                    ],
                    tag="p",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_heading_to_text_node(self):
        text = "# My `awesome` **heading**"
        expected = ParentNode(
            children=[
                ParentNode(
                    children=[
                        LeafNode(value="My "),
                        LeafNode(value="awesome", tag="code"),
                        LeafNode(value=" "),
                        LeafNode(value="heading", tag="b"),
                    ],
                    tag="h1",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_code_to_text_node(self):
        text = """```\nprint("Hello World")\n```"""
        expected = ParentNode(
            children=[
                LeafNode(
                    value="""\nprint("Hello World")\n""",
                    tag="pre",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(markdown_to_html_node(text=text).to_html(), expected)


if __name__ == "__main__":
    unittest.main()
