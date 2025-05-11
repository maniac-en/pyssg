import os
import sys
from src.core.utils import build_site
from src.core.server import run

# Determine the root path based on "main.py" and other desired paths which will
# later be used for site-code generation and hot-reloading!
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
STATIC_DIR = os.path.join(ROOT_PATH, "src/static")
BUILD_DIR = os.path.join(ROOT_PATH, "docs")
CONTENT_DIR = os.path.join(ROOT_PATH, "content")
TEMPLATE_PATH = os.path.join(ROOT_PATH, "template.html")
BASE_PATH = sys.argv[1] if len(sys.argv) == 2 else "/"

build_site_handler = build_site(
    static_dir=STATIC_DIR,
    content_dir=CONTENT_DIR,
    template_path=TEMPLATE_PATH,
    dest_path=BUILD_DIR,
    base_path=BASE_PATH
)

if __name__ == "__main__":
    if BASE_PATH != "/":
        build_site_handler()
    else:
        run(
            root_path=ROOT_PATH,
            build_dir=BUILD_DIR,
            build_site_handler=build_site_handler,
        )
