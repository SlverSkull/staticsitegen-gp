import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_empty(self):
        node = HTMLNode()
        expected = ""
        self.assertEqual(node.props_to_html(), expected)

    def test_keys(self):
        node = HTMLNode(props={"key": "value", "Skyrim": "V", 11010: 26})
        expected = ' key="value" Skyrim="V" 11010="26"'
        self.assertEqual(node.props_to_html(), expected)

    def test_1_tag_1_value_5_keys(self):
        node = HTMLNode(
            tag="Elder Scrolls",
            value=5,
            props={"Arena": "I", "Daggerfall": "II", "Morrowind": "III", "Oblivion": "IV", "Skyrim": "V"}
        )
        expected = ' Arena="I" Daggerfall="II" Morrowind="III" Oblivion="IV" Skyrim="V"'
        self.assertEqual(node.props_to_html(), expected)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_img(self):
        node = LeafNode("img", "LEGO", {"src": "https://assets.lego.com/logos/v4.5.0/brand-lego.svg"})
        self.assertEqual(node.to_html(), '<img src="https://assets.lego.com/logos/v4.5.0/brand-lego.svg">LEGO</img>')

    def test_leaf_to_html_raw(self):
        node = LeafNode(None, "Ninjago")
        self.assertEqual(node.to_html(), "Ninjago")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )