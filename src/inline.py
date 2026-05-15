import re
from enum import Enum
from textnode import TextType, TextNode, textnode_to_htmlnode
from htmlnode import HTMLNode, LeafNode, ParentNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for i in old_nodes:
        if i.text_type != TextType.TEXT:
            new_nodes.append(i)
        else:
            split = i.text.split(delimiter)
            if len(split) % 2 == 0:
                raise Exception("Invalid syntax, no closing delimiter...")
            for l in range(len(split)):
                if l % 2 == 0:
                    new_nodes.append(TextNode(split[l], TextType.TEXT))
                else:
                    new_nodes.append(TextNode(split[l], text_type))
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for i in old_nodes:
        image_re = extract_markdown_images(i.text)
        if image_re == [] and i.text != "":
            new_nodes.append(i)
        else:
            temp = i.text
            for l in image_re:
                split = temp.split(f"![{l[0]}]({l[1]})", 1)
                if split[0] != "":
                    new_nodes.append(TextNode(split[0], TextType.TEXT))
                new_nodes.append(TextNode(l[0], TextType.IMAGE, l[1]))
                temp = split[1]
            if temp != "":
                new_nodes.append(TextNode(temp, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for i in old_nodes:
        link_re = extract_markdown_links(i.text)
        if link_re == [] and i.text != "":
            new_nodes.append(i)
        else:
            temp = i.text
            for l in link_re:
                split = temp.split(f"[{l[0]}]({l[1]})", 1)
                if split[0] != "":
                    new_nodes.append(TextNode(split[0], TextType.TEXT))
                new_nodes.append(TextNode(l[0], TextType.LINK, l[1]))
                temp = split[1]
            if temp != "":
                new_nodes.append(TextNode(temp, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    code_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
    bold_nodes = split_nodes_delimiter(code_nodes, "**", TextType.BOLD)
    italic_nodes = split_nodes_delimiter(bold_nodes, "_", TextType.ITALIC)
    image_nodes = split_nodes_image(italic_nodes)
    link_nodes = split_nodes_link(image_nodes)
    return link_nodes

def markdown_to_blocks(markdown):
    final = []
    split = markdown.split("\n\n")
    for s in split:
        s = s.strip()
        if s != "":
            final.append(s)
    return final

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    elif block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    elif block.startswith(">"):
        split = block.split("\n")
        for s in split:
            if not s.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    elif block.startswith("- "):
        split = block.split("\n")
        for s in split:
            if not s.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED_LIST
    elif block.startswith("1. "):
        split = block.split("\n")
        count = 1
        for s in split:
            if not s.startswith(f"{count}. "):
                return BlockType.PARAGRAPH
            count += 1
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def text_to_children(text):
    textnodes = text_to_textnodes(text)
    htmlnodes = []
    for node in textnodes:
        htmlnodes.append(textnode_to_htmlnode(node))
    return htmlnodes

def block_type_to_html(block, block_type):
    match block_type:
        case BlockType.PARAGRAPH:
            block = block.replace("\n", " ")
            return ParentNode(tag="p", children=text_to_children(block))
        case BlockType.HEADING:
            count = 0
            for i in block[:6]:
                if i == "#":
                    count += 1
            block = block[count + 1:].strip()
            return ParentNode(tag=f"h{count}", children=text_to_children(block))
        case BlockType.CODE:
            node = TextNode(block[4:-3], TextType.TEXT)
            return ParentNode(tag="pre", children=[ParentNode(tag="code", children=[textnode_to_htmlnode(node)])])
        case BlockType.QUOTE:
            lines = block.split("\n")
            lines_sliced = []
            for line in lines:
                lines_sliced.append(line[1:].strip())
            block = "\n".join(lines_sliced)
            return ParentNode(tag="blockquote", children=text_to_children(block))
        case BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            line_nodes = []
            for line in lines:
                line_nodes.append(ParentNode(tag="li", children=text_to_children(line[2:].strip())))
            return ParentNode(tag="ul", children=line_nodes)
        case BlockType.ORDERED_LIST:
            lines = block.split("\n")
            line_nodes = []
            for line in lines:
                prefix = line.index(". ") + 2
                line_nodes.append(ParentNode(tag="li", children=text_to_children(line[prefix:].strip())))
            return ParentNode(tag="ol", children=line_nodes)

def markdown_to_html_node(markdown):
    children = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        block_type = block_to_block_type(block)
        node = block_type_to_html(block, block_type)
        children.append(node)
    return ParentNode(tag="div", children=children)

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block.startswith("# "):
            return block[2:].strip()
    raise Exception("No title in markdown file...")