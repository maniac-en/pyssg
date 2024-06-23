import unittest
from typing import Dict, List, Optional
from src.core.htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNodeInitialization(unittest.TestCase):
    def test_valid_initialization(self):
        node = HTMLNode(tag="div", value="Hello", props={"class": "container"})
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {"class": "container"})

    def test_initialization_with_children(self):
        child = HTMLNode(tag="span", value="World")
        node_with_children = HTMLNode(tag="div", value="Hello", children=[child])
        self.assertEqual(node_with_children.children, [child])

    def test_invalid_tag_type(self):
        with self.assertRaises(ValueError):
            HTMLNode(tag=123)

    def test_invalid_value_type(self):
        with self.assertRaises(ValueError):
            HTMLNode(value=123)

    def test_invalid_children_type(self):
        with self.assertRaises(ValueError):
            HTMLNode(children="not a list")

    def test_invalid_child_type(self):
        with self.assertRaises(ValueError):
            HTMLNode(children=["not a HTMLNode"])

    def test_invalid_props_type(self):
        with self.assertRaises(ValueError):
            HTMLNode(props="not a dict")


class TestHTMLNodePropsToHtml(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"id": "main", "class": "container"})
        self.assertEqual(node.props_to_html(), 'id="main" class="container"')

    def test_to_html_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestHTMLNodeRepr(unittest.TestCase):
    def test_repr(self):
        child = HTMLNode(tag="span", value="World")
        node = HTMLNode(
            tag="div", value="Hello", children=[child], props={"id": "main"}
        )
        expected_repr = """HTMLNode(
  Tag: div,
  Value: Hello,
  Children: [
    HTMLNode(
      Tag: span,
      Value: World,
      Children: [
None
      ],
      Props: {  }
    )
  ],
  Props: { "id": "main" }
)"""
        self.assertEqual(node.__repr__(), expected_repr)


class TestLeafNodeInitialization(unittest.TestCase):
    def test_valid_initialization(self):
        leaf = LeafNode(value="Text", tag="p", props={"class": "text"})
        self.assertEqual(leaf.tag, "p")
        self.assertEqual(leaf.value, "Text")
        self.assertEqual(leaf.children, [])
        self.assertEqual(leaf.props, {"class": "text"})

    def test_invalid_initialization(self):
        with self.assertRaises(ValueError):
            LeafNode(value=None)


class TestLeafNodeToHtml(unittest.TestCase):
    def test_to_html_no_tag(self):
        leaf_no_tag = LeafNode(value="Text")
        self.assertEqual(leaf_no_tag.to_html(), "Text")

    def test_to_html_with_tag_no_props(self):
        leaf_no_props = LeafNode(value="Text", tag="p")
        self.assertEqual(leaf_no_props.to_html(), "<p>Text</p>")

    def test_to_html_with_tag_and_props(self):
        leaf_with_props = LeafNode(value="Text", tag="p", props={"class": "text"})
        self.assertEqual(leaf_with_props.to_html(), '<p class="text">Text</p>')

    def test_to_html_img_tag_with_props(self):
        leaf_img = LeafNode(
            value="",
            tag="img",
            props={"src": "http://example.com/image.jpg", "alt": "Image"},
        )
        self.assertEqual(
            leaf_img.to_html(), '<img src="http://example.com/image.jpg" alt="Image" />'
        )

    def test_to_html_other_tag_with_props(self):
        leaf_with_props = LeafNode(
            value="Link", tag="a", props={"href": "http://example.com"}
        )
        self.assertEqual(
            leaf_with_props.to_html(), '<a href="http://example.com">Link</a>'
        )


class TestParentNodeInitialization(unittest.TestCase):
    def test_valid_initialization(self):
        child1 = LeafNode(value="Child 1", tag="span")
        child2 = LeafNode(value="Child 2", tag="span")
        parent = ParentNode(
            children=[child1, child2], tag="div", props={"class": "container"}
        )
        self.assertEqual(parent.tag, "div")
        self.assertEqual(parent.children, [child1, child2])
        self.assertEqual(parent.props, {"class": "container"})

    def test_invalid_initialization_missing_tag(self):
        with self.assertRaises(ValueError):
            ParentNode(children=[LeafNode(value="Child 1")])

    def test_invalid_initialization_missing_children(self):
        with self.assertRaises(ValueError):
            ParentNode(children=[], tag="div")

    def test_invalid_initialization_missing_children_and_tag(self):
        with self.assertRaises(ValueError):
            ParentNode(children=None, tag="div")


class TestParentNodeToHtml(unittest.TestCase):
    def test_to_html_with_props(self):
        child1 = LeafNode(value="Child 1", tag="span")
        child2 = LeafNode(value="Child 2", tag="span")
        parent = ParentNode(
            children=[child1, child2], tag="div", props={"class": "container"}
        )
        self.assertEqual(
            parent.to_html(),
            '<div class="container"><span>Child 1</span><span>Child 2</span></div>',
        )

    def test_to_html_without_props(self):
        child1 = LeafNode(value="Child 1", tag="span")
        child2 = LeafNode(value="Child 2", tag="span")
        parent = ParentNode(children=[child1, child2], tag="div")
        self.assertEqual(
            parent.to_html(), "<div><span>Child 1</span><span>Child 2</span></div>"
        )


if __name__ == "__main__":
    unittest.main()
