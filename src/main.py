import os, shutil, sys

from textnode import TextNode, TextType
from inline import markdown_to_html_node, extract_title

basepath = "/"
if len(sys.argv) > 1:
    basepath = sys.argv[1]

def copy_files(src, dst):
    if not os.path.exists(dst):
        os.mkdir(dst)

    for f in os.listdir(src):
        src_path = os.path.join(src, f)
        dst_path = os.path.join(dst, f)
        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
        else:
            copy_files(src_path, dst_path)

def copy_static():
    docs = "docs"
    static = "static"
    if os.path.exists(docs):
        shutil.rmtree(docs)
    copy_files(static, docs)

def generate_page(src, dst, tmp, bsp):
    print(f"Generating page from {src} to {dst} using {tmp}")
    with open(src) as f:
        src_read = f.read()
    with open(tmp) as f:
        tmp_read = f.read()
    html = markdown_to_html_node(src_read).to_html()
    title = extract_title(src_read)
    replaced = tmp_read.replace("{{ Title }}", title).replace("{{ Content }}", html).replace('href="/', f'href="{bsp}').replace('src="/', f'src="{bsp}')
    os.makedirs(os.path.dirname(dst), exist_ok = True)
    with open(dst, "w") as f:
        f.write(replaced)

def generate_pages(src, dst, tmp, bsp):
    if not os.path.exists(dst):
        os.mkdir(dst)
    
    for f in os.listdir(src):
        src_path = os.path.join(src, f)
        dst_path = os.path.join(dst, f)
        if os.path.isfile(src_path):
            if src_path.endswith(".md"):
                dst_path = dst_path[:-3] + ".html"
                generate_page(src_path, dst_path, tmp, bsp)
        else:
            generate_pages(src_path, dst_path, tmp, bsp)

def main():
    copy_static()
    generate_pages("content", "docs", "template.html", basepath)

main()