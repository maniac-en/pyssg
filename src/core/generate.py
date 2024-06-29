import os
from src.core.markdown_functions import markdown_to_html_node


def extract_title(text: str) -> str:
    text_split = text.split(sep="# ", maxsplit=1)[0]
    if text_split == text:
        raise ValueError("Inalid markdown without any h1 header")
    return text_split[1].split("\n")[0]


def generate_page(src_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {src_path} to {dest_path} using {template_path}")

    # read markdown source
    with open(src_path, "r") as f:
        src = f.read()
        f.close()

    # read template file
    with open(template_path, "r") as f:
        templ = f.read()
        f.close()

    html_content = markdown_to_html_node(src).to_html()
    title = "Tolkien Fan Club"

    templ = templ.replace("{{ Title }}", title)
    templ = templ.replace("{{ Content }}", html_content)

    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path))

    with open(dest_path, "w") as f:
        f.write(templ)
        f.close()


def generate_page_recursive(content_path: str, template_path: str, dest_path: str):
    if os.path.isdir(content_path):
        for file in os.listdir(content_path):
            content_src = os.path.join(content_path, file)
            dest_file = os.path.join(dest_path, file)[:-2] + "html"
            if os.path.isfile(content_src):
                generate_page(content_src, template_path, dest_file)
            elif os.path.isdir(content_src):
                new_dest_path = os.path.join(dest_path, file)
                os.mkdir(new_dest_path)
                generate_page_recursive(content_src, template_path, new_dest_path)
