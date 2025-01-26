import os
import sys
import argparse
from src.core.utils import build_site
from src.core.server import run
from src.core.config import Config


def parse_args():
    parser = argparse.ArgumentParser(description='Python Static Site Generator')
    parser.add_argument('--config', '-c', type=str, help='Path to config file')
    parser.add_argument('--base-path', '-b', type=str, help='Base path for site (overrides config)')
    parser.add_argument('--build-only', action='store_true', help='Build site only (no server)')
    parser.add_argument('--port', '-p', type=int, help='Server port (overrides config)')
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        config = Config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure pyssg.config.json exists in the current directory or specify with --config")
        sys.exit(1)
    
    # Override config with command line arguments
    base_path = args.base_path if args.base_path else config.base_path
    server_port = args.port if args.port else config.server_port
    
    # Legacy support: if first argument is provided and no --base-path, use it as base_path
    if len(sys.argv) >= 2 and not args.base_path and not sys.argv[1].startswith('-'):
        base_path = sys.argv[1]
    
    # Disable hot reload for production builds
    enable_hot_reload = config.enable_hot_reload and not args.build_only and base_path == "/"
    
    build_site_handler = build_site(
        static_dir=config.static_dir,
        content_dir=config.content_dir,
        template_path=config.template_path,
        dest_path=config.build_dir,
        base_path=base_path,
        css_path=config.css_path,
        enable_hot_reload=enable_hot_reload
    )
    
    if args.build_only or base_path != "/":
        build_site_handler()
    else:
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        run(
            root_path=root_path,
            build_dir=config.build_dir,
            build_site_handler=build_site_handler,
            port=server_port
        )


if __name__ == "__main__":
    main()
