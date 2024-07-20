import unittest

import src.core.markdown_functions as mf
import src.core.text_functions as tf
from src.core.htmlnode import LeafNode, ParentNode
from src.core.textnode import TextNode


class TestExtractMarkdownImages(unittest.TestCase):
    def test_only_image(self):
        text = "![alt text](http://example.com/image.jpg)"
        expected = [("alt text", "http://example.com/image.jpg")]
        self.assertEqual(mf.extract_markdown_images(text), expected)

    def test_single_image(self):
        text = "This is an image ![alt text](http://example.com/image.jpg)."
        expected = [("alt text", "http://example.com/image.jpg")]
        self.assertEqual(mf.extract_markdown_images(text), expected)

    def test_multiple_images(self):
        text = "This is an image ![alt text](http://example.com/image.jpg). Here is another ![another image](https://example.org/pic.png)."
        expected = [
            ("alt text", "http://example.com/image.jpg"),
            ("another image", "https://example.org/pic.png"),
        ]
        self.assertEqual(mf.extract_markdown_images(text), expected)

    def test_no_images(self):
        text = "No images here!"
        expected = []
        self.assertEqual(mf.extract_markdown_images(text), expected)

    def test_broken_images(self):
        text = "Broken ![alt text(http://example.com/image.jpg)."
        expected = []
        self.assertEqual(mf.extract_markdown_images(text), expected)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_only_link(self):
        text = "[link](http://example.com)"
        expected = [("link", "http://example.com")]
        self.assertEqual(mf.extract_markdown_links(text), expected)

    def test_single_link(self):
        text = "This is a [link](http://example.com)."
        expected = [("link", "http://example.com")]
        self.assertEqual(mf.extract_markdown_links(text), expected)

    def test_multiple_links(self):
        text = "This is a [link](http://example.com). Here is another [another link](https://example.org)."
        expected = [
            ("link", "http://example.com"),
            ("another link", "https://example.org"),
        ]
        self.assertEqual(mf.extract_markdown_links(text), expected)

    def test_no_links(self):
        text = "No links here!"
        expected = []
        self.assertEqual(mf.extract_markdown_links(text), expected)

    def test_broken_links(self):
        text = "Broken [link(http://example.com)."
        expected = []
        self.assertEqual(mf.extract_markdown_links(text), expected)


class TestGetCodeblockIndices(unittest.TestCase):
    def test_single_codeblock(self):
        text = "```\ncode block\n```"
        expected = [(0, 18)]
        self.assertEqual(mf.get_codeblock_indices(text), expected)

    def test_multiple_codeblocks(self):
        text = "```\ncode block 1\n```\n\n```\ncode block 2\n```"
        expected = [(0, 20), (22, 42)]
        self.assertEqual(mf.get_codeblock_indices(text), expected)

    def test_no_codeblocks(self):
        text = "This is a paragraph."
        expected = []
        self.assertEqual(mf.get_codeblock_indices(text), expected)

    def test_incomplete_codeblock(self):
        text = "```\ncode block"
        expected = []
        self.assertEqual(mf.get_codeblock_indices(text), expected)


class TestGetNonCodeblocks(unittest.TestCase):
    def test_single_paragraph(self):
        text = "This is a paragraph."
        expected = ["This is a paragraph."]
        self.assertEqual(mf.get_non_codeblocks(text), expected)

    def test_multiple_paragraphs(self):
        text = "This is a paragraph.\n\nThis is another paragraph."
        expected = ["This is a paragraph.", "This is another paragraph."]
        self.assertEqual(mf.get_non_codeblocks(text), expected)

    def test_mixed_content(self):
        text = """\
This is a paragraph.

> This is a quote.

* This is a list item
* Another list item\
        """
        expected = [
            "This is a paragraph.",
            "> This is a quote.",
            "* This is a list item\n* Another list item",
        ]
        self.assertEqual(mf.get_non_codeblocks(text), expected)

    def test_codeblock_in_text(self):
        text = "Paragraph before\n```\ncode block\n```\nParagraph after"
        expected = ["Paragraph before\n```\ncode block\n```\nParagraph after"]
        self.assertEqual(mf.get_non_codeblocks(text), expected)

    def test_empty_input(self):
        text = ""
        expected = []
        self.assertEqual(mf.get_non_codeblocks(text), expected)


class TestConvertMarkdownToBlock(unittest.TestCase):
    def test_single_paragraph(self):
        text = "This is a paragraph."
        expected = ["This is a paragraph."]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_multiple_paragraphs(self):
        text = """
        This is a paragraph.

        This is another paragraph.
        """
        expected = ["This is a paragraph.", "This is another paragraph."]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_list_items(self):
        text = """
        * Item 1
        * Item 2
        """
        expected = ["* Item 1\n* Item 2"]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_empty_input(self):
        text = ""
        expected = []
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_only_newlines(self):
        text = "\n\n\n"
        expected = []
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_codeblock_only(self):
        text = "```\ncode block\n```"
        expected = ["```\ncode block\n```"]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_codeblock_with_text(self):
        text = "Paragraph before\n```\ncode block\n```\nParagraph after"
        expected = ["Paragraph before", "```\ncode block\n```", "Paragraph after"]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_quote_block(self):
        text = "> This is a quote"
        expected = ["> This is a quote"]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_heading(self):
        text = "# This is a heading"
        expected = ["# This is a heading"]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_ordered_list(self):
        text = "1. First item\n2. Second item"
        expected = ["1. First item\n2. Second item"]
        self.assertEqual(mf.markdown_to_blocks(text), expected)

    def test_mixed_content(self):
        text = """\
This is **bolded** paragraph

This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

```
def test_empty_input(self):
    text = ""
    expected = []
    self.assertEqual(mf.markdown_to_blocks(text), expected)
```


* This is a list
* with items

> This is a quote.

1. This is also a list
2. with items\
        """
        expected = [
            "This is **bolded** paragraph",
            "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
            """```\ndef test_empty_input(self):\n    text = ""\n    expected = []\n    self.assertEqual(mf.markdown_to_blocks(text), expected)\n```""",
            "* This is a list\n* with items",
            "> This is a quote.",
            "1. This is also a list\n2. with items",
        ]
        self.assertEqual(mf.markdown_to_blocks(text), expected)


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(mf.get_markdown_block_type("# Heading"), mf.BLOCK_TYPE_HEADING)
        self.assertEqual(
            mf.get_markdown_block_type("## Subheading"), mf.BLOCK_TYPE_HEADING
        )
        self.assertEqual(
            mf.get_markdown_block_type("###### Small heading"), mf.BLOCK_TYPE_HEADING
        )

    def test_code(self):
        self.assertEqual(
            mf.get_markdown_block_type("```code block```"), mf.BLOCK_TYPE_CODE
        )
        self.assertEqual(
            mf.get_markdown_block_type("```\nprint('Hello, world!')\n```"),
            mf.BLOCK_TYPE_CODE,
        )

    def test_quote(self):
        self.assertEqual(
            mf.get_markdown_block_type("> This is a quote"), mf.BLOCK_TYPE_QUOTE
        )
        self.assertEqual(
            mf.get_markdown_block_type("> This is a quote\n> with multiple lines"),
            mf.BLOCK_TYPE_QUOTE,
        )

    def test_unordered_list(self):
        self.assertEqual(
            mf.get_markdown_block_type("* Unordered list item"),
            mf.BLOCK_TYPE_UNORD_LIST,
        )
        self.assertEqual(
            mf.get_markdown_block_type("- Another unordered list item"),
            mf.BLOCK_TYPE_UNORD_LIST,
        )
        self.assertEqual(
            mf.get_markdown_block_type("* List item\n* Another list item"),
            mf.BLOCK_TYPE_UNORD_LIST,
        )

    def test_ordered_list(self):
        self.assertEqual(
            mf.get_markdown_block_type("1. Ordered list item"), mf.BLOCK_TYPE_ORD_LIST
        )
        self.assertEqual(
            mf.get_markdown_block_type("1. First item\n2. Second item\n3. Third item"),
            mf.BLOCK_TYPE_ORD_LIST,
        )

    def test_paragraph(self):
        self.assertEqual(
            mf.get_markdown_block_type("Just a paragraph."), mf.BLOCK_TYPE_PARAGRAPH
        )
        self.assertEqual(
            mf.get_markdown_block_type("This is a **bold** text."),
            mf.BLOCK_TYPE_PARAGRAPH,
        )
        self.assertEqual(
            mf.get_markdown_block_type("#Heading without space"),
            mf.BLOCK_TYPE_PARAGRAPH,
        )

    def test_invalid_heading(self):
        self.assertEqual(
            mf.get_markdown_block_type("####### Invalid heading"),
            mf.BLOCK_TYPE_PARAGRAPH,
        )

    def test_invalid_quote(self):
        self.assertEqual(
            mf.get_markdown_block_type("> line 1\nline without >\n> line 2"),
            mf.BLOCK_TYPE_PARAGRAPH,
        )

    def test_invalid_unordered_list(self):
        self.assertEqual(
            mf.get_markdown_block_type("* line 1\nline without *\n* line 2"),
            mf.BLOCK_TYPE_PARAGRAPH,
        )

    def test_invalid_ordered_list(self):
        self.assertEqual(
            mf.get_markdown_block_type("1 Not an ordered list"), mf.BLOCK_TYPE_PARAGRAPH
        )
        self.assertEqual(
            mf.get_markdown_block_type("1. First item\n3. Third item"),
            mf.BLOCK_TYPE_PARAGRAPH,
        )


class TestMarkdownToTextNode(unittest.TestCase):
    def test_paragraph_single_line(self):
        text = "This is **bolded** paragraph"
        expected_nodes = [
            TextNode("This is ", tf.TEXT_TYPE_TEXT),
            TextNode("bolded", tf.TEXT_TYPE_BOLD),
            TextNode(" paragraph", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(mf.markdown_paragraph_to_text_node(text=text), expected_nodes)

    def test_paragraph_multi_line(self):
        text = """\
This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line\
"""
        expected_nodes = [
            TextNode("This is another paragraph with ", tf.TEXT_TYPE_TEXT),
            TextNode("italic", tf.TEXT_TYPE_ITALIC),
            TextNode(" text and ", tf.TEXT_TYPE_TEXT),
            TextNode("code", tf.TEXT_TYPE_CODE),
            TextNode(
                " here\nThis is the same paragraph on a new line", tf.TEXT_TYPE_TEXT
            ),
        ]
        self.assertEqual(mf.markdown_paragraph_to_text_node(text=text), expected_nodes)

    def test_heading_plain_h1(self):
        text = "# heading1"
        expected_nodes = [TextNode("heading1", tf.TEXT_TYPE_TEXT)]
        self.assertEqual(mf.markdown_heading_to_text_node(text=text), expected_nodes)

    def test_heading_italic_h2(self):
        text = "## *heading2*"
        expected_nodes = [TextNode("heading2", tf.TEXT_TYPE_ITALIC)]
        self.assertEqual(mf.markdown_heading_to_text_node(text=text), expected_nodes)

    def test_heading_bold_h3(self):
        text = "### **heading3**"
        expected_nodes = [TextNode("heading3", tf.TEXT_TYPE_BOLD)]
        self.assertEqual(mf.markdown_heading_to_text_node(text=text), expected_nodes)

    def test_heading_mix_h4(self):
        text = "#### `heading4` with **bold** word"
        expected_nodes = [
            TextNode("heading4", tf.TEXT_TYPE_CODE),
            TextNode(" with ", tf.TEXT_TYPE_TEXT),
            TextNode("bold", tf.TEXT_TYPE_BOLD),
            TextNode(" word", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(mf.markdown_heading_to_text_node(text=text), expected_nodes)

    def test_heading_invalid_heading(self):
        text = "####### heading7 doesn't exist"
        expected_nodes = [TextNode("####### heading7 doesn't exist", tf.TEXT_TYPE_TEXT)]
        self.assertEqual(mf.markdown_heading_to_text_node(text=text), expected_nodes)

    def test_quote_single_line(self):
        text = "> This is *italic* **bold** word"
        expected_nodes = [
            TextNode("This is ", tf.TEXT_TYPE_TEXT),
            TextNode("italic", tf.TEXT_TYPE_ITALIC),
            TextNode(" ", tf.TEXT_TYPE_TEXT),
            TextNode("bold", tf.TEXT_TYPE_BOLD),
            TextNode(" word", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(mf.markdown_quote_to_text_node(text=text), expected_nodes)

    def test_quote_multi_line(self):
        text = "> This is *italic* **bold** word\n> \n> `codeblock`"
        expected_nodes = [
            TextNode("This is ", tf.TEXT_TYPE_TEXT),
            TextNode("italic", tf.TEXT_TYPE_ITALIC),
            TextNode(" ", tf.TEXT_TYPE_TEXT),
            TextNode("bold", tf.TEXT_TYPE_BOLD),
            TextNode(" word\n\n", tf.TEXT_TYPE_TEXT),
            TextNode("codeblock", tf.TEXT_TYPE_CODE),
        ]
        self.assertEqual(mf.markdown_quote_to_text_node(text=text), expected_nodes)

    def test_quote_nested_quote(self):
        text = "> This quote itself has a > inside it"
        expected_nodes = [
            TextNode("This quote itself has a > inside it", tf.TEXT_TYPE_TEXT)
        ]
        self.assertEqual(mf.markdown_quote_to_text_node(text=text), expected_nodes)

    def test_quote_empty_quote(self):
        text = "> "
        with self.assertRaises(NotImplementedError):
            mf.markdown_quote_to_text_node(text)

    def test_unord_list_single_line(self):
        text = "* **yet to add**: `important code`"
        expected_nodes = [
            [
                TextNode("yet to add", tf.TEXT_TYPE_BOLD),
                TextNode(": ", tf.TEXT_TYPE_TEXT),
                TextNode("important code", tf.TEXT_TYPE_CODE),
            ]
        ]
        self.assertEqual(mf.markdown_unord_list_to_text_node(text=text), expected_nodes)

    def test_unord_list_multi_line(self):
        text = "* item1\n* item2\n* item3"
        expected_nodes = [
            [TextNode("item1", tf.TEXT_TYPE_TEXT)],
            [TextNode("item2", tf.TEXT_TYPE_TEXT)],
            [TextNode("item3", tf.TEXT_TYPE_TEXT)],
        ]
        self.assertEqual(mf.markdown_unord_list_to_text_node(text=text), expected_nodes)

    def test_unord_list_empty(self):
        text = "* "
        with self.assertRaises(NotImplementedError):
            mf.markdown_unord_list_to_text_node(text=text)

    def test_ord_list_single_line(self):
        text = "1. **yet to add**: `important code`"
        expected_nodes = [
            [
                TextNode("yet to add", tf.TEXT_TYPE_BOLD),
                TextNode(": ", tf.TEXT_TYPE_TEXT),
                TextNode("important code", tf.TEXT_TYPE_CODE),
            ]
        ]
        self.assertEqual(mf.markdown_ord_list_to_text_node(text=text), expected_nodes)

    def test_ord_list_multi_line(self):
        text = "1. item1\n2. item2\n3. item3"
        expected_nodes = [
            [TextNode("item1", tf.TEXT_TYPE_TEXT)],
            [TextNode("item2", tf.TEXT_TYPE_TEXT)],
            [TextNode("item3", tf.TEXT_TYPE_TEXT)],
        ]
        self.assertEqual(mf.markdown_ord_list_to_text_node(text=text), expected_nodes)

    def test_ord_list_empty(self):
        text = "1. "
        with self.assertRaises(NotImplementedError):
            mf.markdown_ord_list_to_text_node(text=text)


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
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_paragraph_multi_line(self):
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
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_heading(self):
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
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_code(self):
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
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_quote(self):
        text = "> This is *italic* **bold** word\n> This also has >\n> `codeblock`"
        expected = ParentNode(
            children=[
                ParentNode(
                    children=[
                        LeafNode(value="This is "),
                        LeafNode(value="italic", tag="i"),
                        LeafNode(value=" "),
                        LeafNode(value="bold", tag="b"),
                        LeafNode(value=" word\nThis also has >\n"),
                        LeafNode(value="codeblock", tag="code"),
                    ],
                    tag="blockquote",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_unord_list(self):
        text = "* **bold** item1\n* *italic_item2*\n* item3"
        expected = ParentNode(
            children=[
                ParentNode(
                    children=[
                        ParentNode(
                            children=[
                                LeafNode(value="bold", tag="b"),
                                LeafNode(value=" item1"),
                            ],
                            tag="li",
                        ),
                        ParentNode(
                            children=[
                                LeafNode(value="italic_item2", tag="i"),
                            ],
                            tag="li",
                        ),
                        ParentNode(children=[LeafNode(value="item3")], tag="li"),
                    ],
                    tag="ul",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_ord_list(self):
        text = "1. **bold** item1\n2. *italic_item2*\n3. item3"
        expected = ParentNode(
            children=[
                ParentNode(
                    children=[
                        ParentNode(
                            children=[
                                LeafNode(value="bold", tag="b"),
                                LeafNode(value=" item1"),
                            ],
                            tag="li",
                        ),
                        ParentNode(
                            children=[
                                LeafNode(value="italic_item2", tag="i"),
                            ],
                            tag="li",
                        ),
                        ParentNode(children=[LeafNode(value="item3")], tag="li"),
                    ],
                    tag="ol",
                )
            ],
            tag="div",
        ).to_html()
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)

    def test_markdown_to_html_empty_string(self):
        text = ""
        with self.assertRaises(ValueError):
            mf.markdown_to_html_node(text=text)

    def test_markdown_to_html_mixed_content(self):
        text = """\
# Heading 1

This is a paragraph with `code`.

> A blockquote with **bold** text.

* Unordered list item 1
* Unordered list item 2

1. Ordered list item 1
2. Ordered list item 2\
"""
        expected = ParentNode(
            children=[
                ParentNode(
                    children=[
                        LeafNode(value="Heading 1"),
                    ],
                    tag="h1",
                ),
                ParentNode(
                    children=[
                        LeafNode(value="This is a paragraph with "),
                        LeafNode(value="code", tag="code"),
                        LeafNode(value="."),
                    ],
                    tag="p",
                ),
                ParentNode(
                    children=[
                        LeafNode(value="A blockquote with "),
                        LeafNode(value="bold", tag="b"),
                        LeafNode(value=" text."),
                    ],
                    tag="blockquote",
                ),
                ParentNode(
                    children=[
                        ParentNode(
                            children=[
                                LeafNode(value="Unordered list item 1"),
                            ],
                            tag="li",
                        ),
                        ParentNode(
                            children=[
                                LeafNode(value="Unordered list item 2"),
                            ],
                            tag="li",
                        ),
                    ],
                    tag="ul",
                ),
                ParentNode(
                    children=[
                        ParentNode(
                            children=[
                                LeafNode(value="Ordered list item 1"),
                            ],
                            tag="li",
                        ),
                        ParentNode(
                            children=[
                                LeafNode(value="Ordered list item 2"),
                            ],
                            tag="li",
                        ),
                    ],
                    tag="ol",
                ),
            ],
            tag="div",
        ).to_html()
        self.assertEqual(mf.markdown_to_html_node(text=text).to_html(), expected)


if __name__ == "__main__":
    unittest.main()
