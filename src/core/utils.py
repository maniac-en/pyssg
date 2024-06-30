import os
import shutil


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
