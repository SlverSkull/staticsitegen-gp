import unittest

from textnode import TextNode, TextType, textnode_to_htmlnode
from inline import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, markdown_to_html_node, extract_title


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("This is a bold text node", TextType.BOLD)
        node2 = TextNode("This is a bold text node", TextType.BOLD)
        self.assertEqual(node1, node2)
    
    def test_not_eq(self):
        node1 = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is an italic text node", TextType.ITALIC)
        self.assertNotEqual(node1, node2)

    def test_url(self):
        node = TextNode("This is a link node", TextType.LINK, "https://lego.com")
        self.assertIsNotNone(node.url)

    def test_no_url(self):
        node = TextNode("This is a bold text node", TextType.BOLD)
        self.assertIsNone(node.url)

    def test_is_image(self):
        node = TextNode("This is an image node", TextType.IMAGE, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg")
        self.assertIs(node.text_type, TextType.IMAGE)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node")

    def test_italic(self):
        node = TextNode("This is an italic node", TextType.ITALIC)
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node")

    def test_code(self):
        node = TextNode("This is a code node", TextType.CODE)
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_link(self):
        node = TextNode("This is a link node", TextType.LINK, "https://lego.com")
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node")
        self.assertEqual(html_node.props, {"href": "https://lego.com"})

    def test_image(self):
        node = TextNode("This is an image node", TextType.IMAGE, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg")
        html_node = textnode_to_htmlnode(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://assets.lego.com/logos/v4.5.0/brand-lego.svg", "alt": "This is an image node"})
    
    def test_delimiter_code(self):
        node = TextNode("Testing for the `python code` delimiter...", TextType.TEXT)
        delimit_node = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(delimit_node, [TextNode("Testing for the ", TextType.TEXT), TextNode("python code", TextType.CODE), TextNode(" delimiter...", TextType.TEXT)])

    def test_delimiter_bold(self):
        node = TextNode("Testing for the **python bold** delimiter...", TextType.TEXT)
        delimit_node = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(delimit_node, [TextNode("Testing for the ", TextType.TEXT), TextNode("python bold", TextType.BOLD), TextNode(" delimiter...", TextType.TEXT)])
    
    def test_delimiter_italic(self):
        node = TextNode("Testing for the _python italic_ delimiter...", TextType.TEXT)
        delimit_node = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(delimit_node, [TextNode("Testing for the ", TextType.TEXT), TextNode("python italic", TextType.ITALIC), TextNode(" delimiter...", TextType.TEXT)])

    def test_delimiter_odd(self):
        node = TextNode("Testing for the `python code` delimiter...`", TextType.TEXT)
        with self.assertRaises(Exception) as cm:
            delimit_node = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(str(cm.exception), "Invalid syntax, no closing delimiter...")
        
    def test_extract_markdown_images(self):
        matches = extract_markdown_images("This is text with an ![image](https://assets.lego.com/logos/v4.5.0/brand-lego.svg)")
        self.assertListEqual([("image", "https://assets.lego.com/logos/v4.5.0/brand-lego.svg")], matches)
    
    def test_extract_markdown_links(self):
        matches = extract_markdown_links("This is text with a link to [lego](https://lego.com) and to [youtube](https://youtube.com)")
        self.assertListEqual([("lego", "https://lego.com"), ("youtube", "https://youtube.com")], matches)

    def test_extract_markdown_empty(self):
        matches = extract_markdown_images("This is text without an image")
        self.assertListEqual([], matches)
    
    def test_split_nodes_image(self):
        node = TextNode("This is text with an ![image](https://assets.lego.com/logos/v4.5.0/brand-lego.svg)", TextType.TEXT)
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg")
            ]
        )
    
    def test_split_nodes_multi_images(self):
        node = TextNode("This is text with an ![image](https://assets.lego.com/logos/v4.5.0/brand-lego.svg) and another ![image](https://boot.dev/img/bootdev-logo-full-150.png) and no more", TextType.TEXT)
        self.assertEqual(
            split_nodes_image([node]),
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://boot.dev/img/bootdev-logo-full-150.png"),
                TextNode(" and no more", TextType.TEXT)
            ]
        )

    def test_split_multi_nodes_images(self):
        node1 = TextNode("This is text with an ![image](https://assets.lego.com/logos/v4.5.0/brand-lego.svg)", TextType.TEXT)
        node2 = TextNode("This is text with another ![image](https://boot.dev/img/bootdev-logo-full-150.png)", TextType.TEXT)
        self.assertEqual(
            split_nodes_image([node1, node2]),
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg"),
                TextNode("This is text with another ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://boot.dev/img/bootdev-logo-full-150.png")
            ]
        )
    
    def test_split_nodes_link(self):
        node = TextNode("This is text with a [link](https://assets.lego.com/logos/v4.5.0/brand-lego.svg)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg")
            ]
        )
    
    def test_split_nodes_multi_links(self):
        node = TextNode("This is text with a [link](https://assets.lego.com/logos/v4.5.0/brand-lego.svg) and another [link](https://boot.dev/img/bootdev-logo-full-150.png)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node]),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev/img/bootdev-logo-full-150.png")
            ]
        )

    def test_split_multi_nodes_links(self):
        node1 = TextNode("This is text with a [link](https://assets.lego.com/logos/v4.5.0/brand-lego.svg)", TextType.TEXT)
        node2 = TextNode("This is text with another [link](https://boot.dev/img/bootdev-logo-full-150.png)", TextType.TEXT)
        self.assertEqual(
            split_nodes_link([node1, node2]),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://assets.lego.com/logos/v4.5.0/brand-lego.svg"),
                TextNode("This is text with another ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev/img/bootdev-logo-full-150.png")
            ]
        )
    
    def test_text_to_nodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertEqual(
            text_to_textnodes(text),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev")
            ]
        )

    def test_markdown_to_blocks(self):
        md = """This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items"
            ]
        )
    
    def test_markdown_whitespace(self):
        md = """# Lego 2x2 Brick

   The Lego 2x2 brick is one of the most common parts found in sets.
It is 2 studs long, 2 studs wide, and 3 plates tall.
It can be found in almost every color that the Lego Group produces.    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Lego 2x2 Brick",
                "The Lego 2x2 brick is one of the most common parts found in sets.\nIt is 2 studs long, 2 studs wide, and 3 plates tall.\nIt can be found in almost every color that the Lego Group produces."
            ]
        )

    def test_markdown_newlines(self):
        md="""Newline test



End"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "Newline test",
                "End"
            ]
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_extract_title(self):
        md = """
# Elder Scrolls V: Skyrim

The 5th game in the Elder Scrolls series, created by Bethesda game studios.
"""
        title = extract_title(md)
        self.assertEqual(title, "Elder Scrolls V: Skyrim")

    def test_extract_title_whitespace(self):
        md = """
#          Minecraft                    
"""
        title = extract_title(md)
        self.assertEqual(title, "Minecraft")

if __name__ == "__main__":
    unittest.main()