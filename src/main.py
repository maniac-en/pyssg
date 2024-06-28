import os
import shutil


def main():
    script_path = os.path.realpath(__file__)
    static_dir = os.path.join(os.path.dirname(script_path), "static")
    public_dir = os.path.join(os.path.dirname(os.path.dirname(script_path)), "public")
    copy_static_to_public(static_dir, public_dir)


def copy_static_to_public(static_dir: str, public_dir: str):
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
