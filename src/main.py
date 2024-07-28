import os
from src.core.utils import build_site
from src.core.server import run

# Determine the root path based on "main.py" and other desired paths which will
# later be used for site-code generation and hot-reloading!
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
STATIC_DIR = os.path.join(ROOT_PATH, "src/static")
PUBLIC_DIR = os.path.join(ROOT_PATH, "public")
CONTENT_DIR = os.path.join(ROOT_PATH, "content")
TEMPLATE_PATH = os.path.join(ROOT_PATH, "template.html")

build_site_handler = build_site(
    static_dir=STATIC_DIR,
    content_dir=CONTENT_DIR,
    template_path=TEMPLATE_PATH,
    dest_path=PUBLIC_DIR,
)

if __name__ == "__main__":
    run(
        root_path=ROOT_PATH,
        public_dir=PUBLIC_DIR,
        build_site_handler=build_site_handler,
    )
