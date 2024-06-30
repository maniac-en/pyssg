import os
from src.core.utils import copy_static_to_public, generate_page_recursive
from livereload import Server

if __name__ == "__main__":
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    static_dir = os.path.join(root_path, "src/static")
    public_dir = os.path.join(root_path, "public")
    copy_static_to_public(static_dir, public_dir)

    content_path = os.path.join(root_path, "content")
    template_path = os.path.join(root_path, "template.html")

    generate_page_recursive(
        content_path=content_path,
        template_path=template_path,
        dest_path=public_dir,
    )

    handler = lambda: generate_page_recursive(
        content_path=content_path,
        template_path=template_path,
        dest_path=public_dir,
    )

    server = Server()
    server.watch(content_path, handler)
    server.serve(root=public_dir, restart_delay=1)
