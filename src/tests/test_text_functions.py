import unittest
import src.core.text_functions as tf
from src.core.textnode import TextNode


class TestTextToHtmlNode(unittest.TestCase):
    def test_text(self):
        text_node = TextNode(text="Hello", text_type=tf.TEXT_TYPE_TEXT)
        leaf_node = tf.text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "Hello")

    def test_bold(self):
        text_node = TextNode(text="Bold", text_type=tf.TEXT_TYPE_BOLD)
        leaf_node = tf.text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "<b>Bold</b>")

    def test_italic(self):
        text_node = TextNode(text="Italic", text_type=tf.TEXT_TYPE_ITALIC)
        leaf_node = tf.text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "<i>Italic</i>")

    def test__code(self):
        text_node = TextNode(text="Code", text_type=tf.TEXT_TYPE_CODE)
        leaf_node = tf.text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), "<code>Code</code>")

    def test__link(self):
        text_node = TextNode(
            text="Link", text_type=tf.TEXT_TYPE_LINK, url="http://example.com"
        )
        leaf_node = tf.text_node_to_html_node(text_node)
        self.assertEqual(leaf_node.to_html(), '<a href="http://example.com">Link</a>')

    def test__image(self):
        text_node = TextNode(
            text="Image",
            text_type=tf.TEXT_TYPE_IMAGE,
            url="http://example.com/image.jpg",
        )
        leaf_node = tf.text_node_to_html_node(text_node)
        self.assertEqual(
            leaf_node.to_html(),
            '<img src="http://example.com/image.jpg" alt="Image" />',
        )

    def test_invalid(self):
        text_node = TextNode(text="Invalid", text_type="invalid")
        with self.assertRaises(ValueError):
            tf.text_node_to_html_node(text_node)


class TestSplitNodes(unittest.TestCase):
    def test_without_delimiter(self):
        nodes = [TextNode(text="Hello World", text_type=tf.TEXT_TYPE_TEXT)]
        self.assertEqual(tf.split_nodes_delimiter(nodes, "`", tf.TEXT_TYPE_CODE), nodes)

    def test_with_delimiter(self):
        nodes = [TextNode(text="Hello `code` World", text_type=tf.TEXT_TYPE_TEXT)]
        expected_nodes = [
            TextNode(text="Hello ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="code", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text=" World", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            tf.split_nodes_delimiter(nodes, "`", tf.TEXT_TYPE_CODE), expected_nodes
        )

    def test_with_multiple_delimiters(self):
        nodes = [
            TextNode(
                text="Hello `code` and `more code` World", text_type=tf.TEXT_TYPE_TEXT
            )
        ]
        expected_nodes = [
            TextNode(text="Hello ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="code", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text=" and ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="more code", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text=" World", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            tf.split_nodes_delimiter(nodes, "`", tf.TEXT_TYPE_CODE), expected_nodes
        )

    def test_with_nested_delimiters(self):
        nodes = [
            TextNode(
                text="Hello `code with ``nested`` syntax` World",
                text_type=tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode(text="Hello ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="code with ", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text="nested", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text=" syntax", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text=" World", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            tf.split_nodes_delimiter(nodes, "`", tf.TEXT_TYPE_CODE), expected_nodes
        )

    def test_with_nested_delimiters_and_not_implemented(self):
        nodes = [
            TextNode(
                text="Another **test**.",
                text_type=tf.TEXT_TYPE_TEXT,
            )
        ]
        with self.assertRaises(NotImplementedError):
            tf.split_nodes_delimiter(nodes, "*", tf.TEXT_TYPE_ITALIC)

    def test_with_only_delimited_word(self):
        nodes = [TextNode(text="*italic word*", text_type=tf.TEXT_TYPE_TEXT)]
        expected_nodes = [TextNode(text="italic word", text_type=tf.TEXT_TYPE_ITALIC)]
        self.assertEqual(
            tf.split_nodes_delimiter(nodes, "*", tf.TEXT_TYPE_ITALIC), expected_nodes
        )

    def test_with_nested_bold_delimiters(self):
        nodes = [
            TextNode(
                text="This is an *italic and **bold** word*.",
                text_type=tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode(text="This is an *italic and ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="bold", text_type=tf.TEXT_TYPE_BOLD),
            TextNode(text=" word*.", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(
            tf.split_nodes_delimiter(nodes, "**", tf.TEXT_TYPE_BOLD), expected_nodes
        )


class TestInvalidMarkdownSyntax(unittest.TestCase):
    def test_invalid_markdown_syntax(self):
        nodes = [TextNode(text="Hello `code World", text_type=tf.TEXT_TYPE_TEXT)]
        with self.assertRaises(ValueError):
            tf.split_nodes_delimiter(nodes, "`", tf.TEXT_TYPE_CODE)


class TestSplitNodeImage(unittest.TestCase):
    def test_single_image(self):
        nodes = [
            TextNode(
                "This is text with an ![image](https://example.com/image.jpg)",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is text with an ", tf.TEXT_TYPE_TEXT),
            TextNode(
                "image",
                tf.TEXT_TYPE_IMAGE,
                "https://example.com/image.jpg",
            ),
        ]
        self.assertEqual(tf.split_nodes_image(nodes), expected_nodes)

    def test_multiple_images(self):
        nodes = [
            TextNode(
                "This is an image ![alt text](http://example.com/image.jpg). Here is another ![another image](https://example.org/pic.png).",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is an image ", tf.TEXT_TYPE_TEXT),
            TextNode(
                "alt text",
                tf.TEXT_TYPE_IMAGE,
                "http://example.com/image.jpg",
            ),
            TextNode(". Here is another ", tf.TEXT_TYPE_TEXT),
            TextNode(
                "another image",
                tf.TEXT_TYPE_IMAGE,
                "https://example.org/pic.png",
            ),
            TextNode(".", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.split_nodes_image(nodes), expected_nodes)

    def test_no_images_with_exclamation_sign(self):
        nodes = [
            TextNode(
                "This is text without any images!",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is text without any images!", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.split_nodes_image(nodes), expected_nodes)

    def test_non_text_type(self):
        nodes = [TextNode("This should not be split", tf.TEXT_TYPE_BOLD)]
        expected_nodes = [TextNode("This should not be split", tf.TEXT_TYPE_BOLD)]
        self.assertEqual(tf.split_nodes_image(nodes), expected_nodes)

    def test_broken_image(self):
        nodes = [
            TextNode(
                "This is an image with a broken ![alt text](http://example.com/image.jpg link.",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        self.assertEqual(tf.split_nodes_image(nodes), nodes)


class TestSplitNodeLink(unittest.TestCase):
    def test_single_link(self):
        nodes = [
            TextNode(
                "This is a [link](https://example.com)",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is a ", tf.TEXT_TYPE_TEXT),
            TextNode(
                "link",
                tf.TEXT_TYPE_LINK,
                "https://example.com",
            ),
        ]
        self.assertEqual(tf.split_nodes_link(nodes), expected_nodes)

    def test_multiple_links(self):
        nodes = [
            TextNode(
                "This is a [link](http://example.com). Here is another [another link](https://example.org).",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is a ", tf.TEXT_TYPE_TEXT),
            TextNode(
                "link",
                tf.TEXT_TYPE_LINK,
                "http://example.com",
            ),
            TextNode(". Here is another ", tf.TEXT_TYPE_TEXT),
            TextNode(
                "another link",
                tf.TEXT_TYPE_LINK,
                "https://example.org",
            ),
            TextNode(".", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.split_nodes_link(nodes), expected_nodes)

    def test_no_links(self):
        nodes = [
            TextNode(
                "This is text without any links.",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        expected_nodes = [
            TextNode("This is text without any links.", tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.split_nodes_link(nodes), expected_nodes)

    def test_non_text_type(self):
        nodes = [TextNode("This should not be split", tf.TEXT_TYPE_BOLD)]
        expected_nodes = [TextNode("This should not be split", tf.TEXT_TYPE_BOLD)]
        self.assertEqual(tf.split_nodes_link(nodes), expected_nodes)

    def test_broken_link(self):
        nodes = [
            TextNode(
                "This is a [link](http://example.com text with a broken link.",
                tf.TEXT_TYPE_TEXT,
            )
        ]
        with self.assertRaises(ValueError):
            tf.split_nodes_link(nodes)


class TestTextToTextNode(unittest.TestCase):
    def test_plain_text(self):
        text = "This is a plain text."
        expected = [TextNode(text="This is a plain text.", text_type=tf.TEXT_TYPE_TEXT)]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_bold_text(self):
        text = "This is **bold** text."
        expected = [
            TextNode(text="This is ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="bold", text_type=tf.TEXT_TYPE_BOLD),
            TextNode(text=" text.", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_italic_text(self):
        text = "This is *italic* text."
        expected = [
            TextNode(text="This is ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="italic", text_type=tf.TEXT_TYPE_ITALIC),
            TextNode(text=" text.", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_code_text(self):
        text = "This is `code` text."
        expected = [
            TextNode(text="This is ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="code", text_type=tf.TEXT_TYPE_CODE),
            TextNode(text=" text.", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_image_text(self):
        text = "This is an ![image](http://example.com/image.jpg)."
        expected = [
            TextNode(text="This is an ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(
                text="image",
                text_type=tf.TEXT_TYPE_IMAGE,
                url="http://example.com/image.jpg",
            ),
            TextNode(text=".", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_link_text(self):
        text = "This is a [link](http://example.com)."
        expected = [
            TextNode(text="This is a ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(
                text="link", text_type=tf.TEXT_TYPE_LINK, url="http://example.com"
            ),
            TextNode(text=".", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_combined_markdown(self):
        text = "This is **bold** and *italic* with a [link](http://example.com) and an ![image](http://example.com/image.jpg)."
        expected = [
            TextNode(text="This is ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="bold", text_type=tf.TEXT_TYPE_BOLD),
            TextNode(text=" and ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(text="italic", text_type=tf.TEXT_TYPE_ITALIC),
            TextNode(text=" with a ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(
                text="link", text_type=tf.TEXT_TYPE_LINK, url="http://example.com"
            ),
            TextNode(text=" and an ", text_type=tf.TEXT_TYPE_TEXT),
            TextNode(
                text="image",
                text_type=tf.TEXT_TYPE_IMAGE,
                url="http://example.com/image.jpg",
            ),
            TextNode(text=".", text_type=tf.TEXT_TYPE_TEXT),
        ]
        self.assertEqual(tf.text_line_to_text_nodes(text), expected)

    def test_invalid_syntax(self):
        text = "This is **invalid markdown*."
        with self.assertRaises(ValueError):
            tf.text_line_to_text_nodes(text)


if __name__ == "__main__":
    unittest.main()
