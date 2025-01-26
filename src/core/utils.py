import os
import shutil
import re
from glob import glob
from typing import List, Dict, Callable
from src.core.markdown_functions import markdown_to_html_node


def find_files_rec(
    path: str,
    exclude_dirs: List[str] = [],
    exclude_files: List[str] = [],
    filetypes_to_monitor: List[str] = [],
) -> List[str]:
    files = list()
    for dirpath, dirnames, filenames in os.walk(top=path, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for ft in filetypes_to_monitor:
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if (
                    file_path in glob(os.path.join(dirpath, f"*.{ft}"), recursive=False)
                    and file not in exclude_files
                ):
                    files.append(file_path)
    return files


def find_file_timestamps(files: List[str]) -> Dict[str, float]:
    f_times = dict()
    for file in files:
        f_times[file] = os.path.getmtime(file)
    return f_times


def copy_static_to_public(static_dir, build_dir: str):
    """
    Copy the contents of a static directory to a build directory. If the build directory exists, it will be deleted first.

    Args:
        static_dir (str): The source directory to copy files from.
        build_dir (str): The destination directory to copy files to.
    """
    # remove public directory if exists
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"Deleting {build_dir} because it already exists!")

    # create public directory
    os.mkdir(build_dir)
    print(f"Creating {build_dir}")

    copy_files_rec(static_dir, build_dir)


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


def generate_page(src_path, template_path, dest_path, base_path: str, css_path: str = "/index.css", enable_hot_reload: bool = True) -> None:
    """
    Generates an HTML page from a markdown source file using a template.

    Parameters:
    src_path (str): The path to the markdown source file.
    template_path (str): The path to the HTML template file.
    dest_path (str): The path to save the generated HTML file.
    base_path (str): The path assumed to be the root of build directory

    Returns: None

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

    # Generate hot reload script if enabled
    hot_reload_script = ""
    if enable_hot_reload:
        hot_reload_script = '''<script>
        function checkForUpdate() {
            fetch('/check_update')
                .then(response => {
                    if (response.status === 200) {
                        location.reload();
                    }
                })
                .catch(err => console.error('Error checking for updates:', err));
        }

        setInterval(checkForUpdate, 1000); // Check every second

        window.onload = () => {
            checkForUpdate();
        }
    </script>'''

    # Construct proper CSS path with base path
    if css_path.startswith('/'):
        full_css_path = f"{base_path.rstrip('/')}{css_path}"
    else:
        full_css_path = f"{base_path.rstrip('/')}/{css_path}"
    
    templ = templ.replace("{{ Title }}", title)
    templ = templ.replace("{{ Content }}", html_content)
    templ = templ.replace("{{ CSSPath }}", full_css_path)
    templ = templ.replace("{{ HotReloadScript }}", hot_reload_script)
    
    # Temporarily replace CSS href to protect it from generic replacement
    css_placeholder = "___CSS_HREF_PLACEHOLDER___"
    templ = templ.replace(f'href="{full_css_path}"', f'href="{css_placeholder}"')
    
    # Apply base path to other absolute URLs
    templ = templ.replace('href="/', f'href="{base_path}')
    templ = templ.replace('src="/', f'src="{base_path}')
    
    # Restore the CSS href
    templ = templ.replace(f'href="{css_placeholder}"', f'href="{full_css_path}"')

    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path))

    with open(dest_path, "w") as f:
        f.write(templ)


def generate_page_recursive(
    content_dir, template_path, dest_path, base_path: str, css_path: str = "/index.css", enable_hot_reload: bool = True
) -> None:
    """
    Recursively generates HTML pages from markdown source files in a directory
    using a template.

    Parameters:
    content_dir (str): The path to the directory containing markdown source files.
    template_path (str): The path to the HTML template file.
    dest_path (str): The path to save the generated HTML files.
    base_path (str): The path assumed to be the root of build directory

    Returns: None

    Raises:
    FileNotFoundError: If the content directory or template file does not exist.
    """
    if not os.path.isdir(content_dir):
        raise FileNotFoundError(f"Content directory not found: {content_dir}")
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    for file in os.listdir(content_dir):
        content_src = os.path.join(content_dir, file)
        dest_file = os.path.join(dest_path, file)[:-2] + "html"
        if os.path.isfile(content_src):
            generate_page(content_src, template_path, dest_file, base_path, css_path, enable_hot_reload)
        elif os.path.isdir(content_src):
            new_dest_path = os.path.join(dest_path, file)
            os.makedirs(new_dest_path, exist_ok=True)
            generate_page_recursive(content_src, template_path, new_dest_path, base_path, css_path, enable_hot_reload)


def build_site(
    static_dir, content_dir, template_path, dest_path, base_path: str, css_path: str = "/index.css", enable_hot_reload: bool = True
) -> Callable[[], None]:
    """
    Returns a closure that, when called, copies all static file content from
    `static_dir` to `dest_path` and then generates HTML pages from markdown
    source files in a directory using a defined template at the `base_path`

    The returned closure will:
    1. Copy static files from `static_dir` to `dest_path` at the `base_path`.
    2. Invoke `generate_page_recursive` to generate HTML pages from markdown
       files in `content_dir` using the specified `template_path`.

    Parameters:
    static_dir (str): The path to the directory containing static files such as
                      CSS, images, etc.
    content_dir (str): The path to the directory containing markdown source files.
    template_path (str): The path to the HTML template file.
    dest_path (str): The path to save the generated HTML files.
    base_path (str): The path assumed to be the root of build directory

    Returns:
    Callable[[], None]: A closure that performs the described operations when called.
    """
    def closure():
        # Copy static files every time the closure is called
        copy_static_to_public(static_dir=static_dir, build_dir=dest_path)
        # Generate HTML pages from markdown source files
        generate_page_recursive(
            content_dir=content_dir,
            template_path=template_path,
            dest_path=dest_path,
            base_path=base_path,
            css_path=css_path,
            enable_hot_reload=enable_hot_reload,
        )

    return closure
