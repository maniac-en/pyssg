import os
import shutil
import re
from src.core.markdown_functions import markdown_to_html_node


def copy_static_to_public(static_dir: str, public_dir: str):
    """
    Copy the contents of a static directory to a public directory. If the public directory exists, it will be deleted first.

    Args:
        static_dir (str): The source directory to copy files from.
        public_dir (str): The destination directory to copy files to.
    """
    # remove public directory if exists
    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
        print(f"Deleting {public_dir} because it already exists!")

    # create public directory
    os.mkdir(public_dir)
    print(f"Creating {public_dir}")

    copy_files_rec(static_dir, public_dir)


# copy files recursively
def copy_files_rec(src: str, dst: str):
    """
    Recursively copies files and directories from the source directory to the destination directory.

    Parameters:
    src (str): The path to the source directory.
    dst (str): The path to the destination directory.

    Raises:
    FileNotFoundError: If the source directory does not exist.
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"Source directory not found: {src}")

    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)

    for file in os.listdir(src):
        src_file_or_dir = os.path.join(src, file)
        dst_file_or_dir = os.path.join(dst, file)
        if os.path.isfile(src_file_or_dir):
            print(f"Copying {src_file_or_dir} -> {dst_file_or_dir}")
            shutil.copy(src=src_file_or_dir, dst=dst_file_or_dir)
        elif os.path.isdir(src_file_or_dir):
            if not os.path.exists(dst_file_or_dir):
                os.mkdir(dst_file_or_dir)
                print(f"Creating {dst_file_or_dir}")
            copy_files_rec(src_file_or_dir, dst_file_or_dir)


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

    for file in os.listdir(content_path):
        content_src = os.path.join(content_path, file)
        dest_file = os.path.join(dest_path, file)[:-2] + "html"
        if os.path.isfile(content_src):
            generate_page(content_src, template_path, dest_file)
        elif os.path.isdir(content_src):
            new_dest_path = os.path.join(dest_path, file)
            os.makedirs(new_dest_path, exist_ok=True)
            generate_page_recursive(content_src, template_path, new_dest_path)
