import os
import re
from src.core.markdown_functions import markdown_to_html_node


def extract_title(text: str) -> str:
    """
    Extracts the title from the first markdown h1 header in the given text.

    Parameters:
    text (str): The input text containing markdown content.

    Returns:
    str: The title extracted from the first h1 header.

    Raises:
    ValueError: If no h1 header is found in the input text.
    """
    title = re.search(r"^# +(.+)$", text, re.MULTILINE)
    if not title:
        raise ValueError("Invalid markdown without any h1 header")
    return title.group(1)


def generate_page(src_path: str, template_path: str, dest_path: str):
    """
    Generates an HTML page from a markdown source file using a template.

    Parameters:
    src_path (str): The path to the markdown source file.
    template_path (str): The path to the HTML template file.
    dest_path (str): The path to save the generated HTML file.

    Raises:
    FileNotFoundError: If the markdown source file or template file does not exist.
    ValueError: If the markdown source file does not contain a valid h1 header.
    """
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Markdown source file not found: {src_path}")
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    print(f"Generating page from {src_path} to {dest_path} using {template_path}")

    # read markdown source
    with open(src_path, "r") as f:
        src = f.read()

    # read template file
    with open(template_path, "r") as f:
        templ = f.read()

    html_content = markdown_to_html_node(src).to_html()
    title = extract_title(src)

    templ = templ.replace("{{ Title }}", title)
    templ = templ.replace("{{ Content }}", html_content)

    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path))

    with open(dest_path, "w") as f:
        f.write(templ)


def generate_page_recursive(content_path: str, template_path: str, dest_path: str):
    """
    Recursively generates HTML pages from markdown source files in a directory
    using a template.

    Parameters:
    content_path (str): The path to the directory containing markdown source files.
    template_path (str): The path to the HTML template file.
    dest_path (str): The path to save the generated HTML files.

    Raises:
    FileNotFoundError: If the content directory or template file does not exist.
    """
    if not os.path.isdir(content_path):
        raise FileNotFoundError(f"Content directory not found: {content_path}")
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    if os.path.isdir(content_path):
        for file in os.listdir(content_path):
            content_src = os.path.join(content_path, file)
            dest_file = os.path.join(dest_path, file)[:-2] + "html"
            if os.path.isfile(content_src):
                generate_page(content_src, template_path, dest_file)
            elif os.path.isdir(content_src):
                new_dest_path = os.path.join(dest_path, file)
                os.makedirs(new_dest_path, exist_ok=True)
                generate_page_recursive(content_src, template_path, new_dest_path)
