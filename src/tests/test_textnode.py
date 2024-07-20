import unittest
from src.core.textnode import TextNode


class TestTextNodeInitialization(unittest.TestCase):
    def test_valid_initialization(self):
        node = TextNode(
            text="Hello, World!", text_type="plain", url="http://example.com"
        )
        self.assertEqual(node.text, "Hello, World!")
        self.assertEqual(node.text_type, "plain")
        self.assertEqual(node.url, "http://example.com")

    def test_initialization_without_url(self):
        node_no_url = TextNode(text="Hello, World!", text_type="plain")
        self.assertEqual(node_no_url.text, "Hello, World!")
        self.assertEqual(node_no_url.text_type, "plain")
        self.assertIsNone(node_no_url.url)

    def test_invalid_initialization_missing_text(self):
        with self.assertRaises(ValueError):
            TextNode(text="", text_type="plain")

    def test_invalid_initialization_non_string_text(self):
        with self.assertRaises(ValueError):
            TextNode(text=123, text_type="plain")

    def test_invalid_initialization_missing_text_type(self):
        with self.assertRaises(ValueError):
            TextNode(text="Hello, World!", text_type="")

    def test_invalid_initialization_non_string_text_type(self):
        with self.assertRaises(ValueError):
            TextNode(text="Hello, World!", text_type=123)

    def test_invalid_initialization_non_string_url(self):
        with self.assertRaises(ValueError):
            TextNode(text="Hello, World!", text_type="plain", url=123)


class TestTextNodeEquality(unittest.TestCase):
    def test_equality_of_equal_nodes(self):
        node1 = TextNode(
            text="Hello, World!", text_type="plain", url="http://example.com"
        )
        node2 = TextNode(
            text="Hello, World!", text_type="plain", url="http://example.com"
        )
        self.assertEqual(node1, node2)

    def test_inequality_of_different_nodes(self):
        node1 = TextNode(
            text="Hello, World!", text_type="plain", url="http://example.com"
        )
        node3 = TextNode(
            text="Hello, World!", text_type="markdown", url="http://example.com"
        )
        self.assertNotEqual(node1, node3)


class TestTextNodeRepr(unittest.TestCase):
    def test_repr_with_url(self):
        node = TextNode(
            text="Hello, World!", text_type="plain", url="http://example.com"
        )
        expected_repr = 'TextNode("Hello, World!", plain, http://example.com)'
        self.assertEqual(node.__repr__(), expected_repr)

    def test_repr_without_url(self):
        node_no_url = TextNode(text="Hello, World!", text_type="plain")
        expected_repr_no_url = 'TextNode("Hello, World!", plain, None)'
        self.assertEqual(node_no_url.__repr__(), expected_repr_no_url)


if __name__ == "__main__":
    unittest.main()
