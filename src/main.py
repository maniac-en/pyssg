import os
import shutil

import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from src.core.generate import generate_page_recursive


def main():
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    static_dir = os.path.join(root_path, "src/static")
    public_dir = os.path.join(root_path, "public")
    copy_static_to_public(static_dir, public_dir)

    content_path = os.path.join(root_path, "content")
    template_path = os.path.join(root_path, "template.html")
    generate_page_recursive(
        content_path=content_path, template_path=template_path, dest_path=public_dir
    )


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

    # copy files recursively
    def copy_files(src: str, dst: str):
        for file in os.listdir(src):
            src_file_or_dir = os.path.join(src, file)
            dst_file_or_dir = os.path.join(dst, file)
            if os.path.isfile(src_file_or_dir):
                print(f"Copying {src_file_or_dir} -> {dst_file_or_dir}")
                shutil.copy(src=src_file_or_dir, dst=dst_file_or_dir)
            elif os.path.isdir(src_file_or_dir):
                os.mkdir(dst_file_or_dir)
                print(f"Creating {dst_file_or_dir}")
                copy_files(src_file_or_dir, dst_file_or_dir)

    copy_files(static_dir, public_dir)


main()
