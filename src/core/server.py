from http.server import SimpleHTTPRequestHandler
import socketserver
import os
from typing import Tuple, Set, Callable, List, Dict

from src.core.utils import find_files_rec, find_file_timestamps

HOSTNAME: str = "localhost"
PORT: int = 8080
EXCLUDE_DIRS: List[str] = [
    ".git",
    ".github",
    "__pycache__",
    "venv",
    ".pytest_cache",
    "tests",
    "public",
]
EXCLUDE_FILES: List[str] = ["README.md", "TODO.md"]
FILETYPES_TO_MONITOR: List[str] = ["md", "html", "css", "js"]


def get_updated_tracked_lists(root_path: str) -> Tuple[List[str], Dict[str, float]]:
    """
    Retrieves updated lists of tracked files and their timestamps based on
    the specified root path.

    Args:
    - root_path (str): The root directory path to monitor.

    Returns:
    - Tuple[List[str], Dict[str, float]]: A tuple containing the updated list
      of tracked files and their timestamps.
    """
    files = find_files_rec(
        path=root_path,
        exclude_dirs=EXCLUDE_DIRS,
        exclude_files=EXCLUDE_FILES,
        filetypes_to_monitor=FILETYPES_TO_MONITOR,
    )
    filestamps = find_file_timestamps(files)
    return (files, filestamps)


def compare_files(
    tracked_files: List[str], u_tracked_files: List[str]
) -> Tuple[Set[str], Set[str]]:
    """
    Compares the current tracked files with the updated tracked files
    to identify added and deleted files.

    Args:
    - tracked_files (List[str]): Current list of tracked files.
    - u_tracked_files (List[str]): Updated list of tracked files.

    Returns:
    - Tuple[Set[str], Set[str]]: A tuple containing sets of added and deleted files.
    """
    added_files = set(u_tracked_files) - set(tracked_files)
    deleted_files = set(tracked_files) - set(u_tracked_files)
    return added_files, deleted_files


def compare_timestamps(
    tracked_filestamps: Dict[str, float], u_tracked_filestamps: Dict[str, float]
) -> set[str]:
    """
    Compares the current tracked file timestamps with the updated timestamps
    to identify modified files.

    Args:
    - tracked_filestamps (Dict[str, float]): Current timestamps of tracked files.
    - u_tracked_filestamps (Dict[str, float]): Updated timestamps of tracked files.

    Returns:
    - set[str]: A set of filenames that have been modified.
    """
    modified_files = {
        file
        for file in tracked_filestamps
        if tracked_filestamps[file] != u_tracked_filestamps.get(file)
    }
    return modified_files


def is_needed_to_reload(
    root_path: str,
    tracked_files: List[str],
    tracked_filestamps: Dict[str, float],
) -> bool:
    """
    Checks if a reload of tracked files is needed based on changes in the file system.

    Args:
    - root_path (str): The root directory path to monitor.
    - tracked_files (List[str]): Current list of tracked files.
    - tracked_filestamps (Dict[str, float]): Current timestamps of tracked files.

    Returns:
    - bool: True if a reload is needed, False otherwise.
    """
    u_tracked_files, u_tracked_filestamps = get_updated_tracked_lists(root_path)

    # Check for added or deleted files
    added_files, deleted_files = compare_files(tracked_files, u_tracked_files)
    if added_files or deleted_files:
        print("Added files:", added_files)
        print("Deleted files:", deleted_files)
        return True

    # Check for modified files
    modified_files = compare_timestamps(tracked_filestamps, u_tracked_filestamps)
    if modified_files:
        print("Modified files:", modified_files)
        return True

    return False


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler to serve files and handle reload checks.
    """

    def __init__(self, *args, directory=None, **kwargs):
        """
        Initializes the HTTP request handler.

        Args:
        - *args: Variable length argument list.
        - directory (str, optional): The directory to serve files from. Defaults to None.
        - **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, directory=directory, **kwargs)


def create_handler(
    root_path: str,
    public_dir: str,
    build_handler: Callable[[], None],
    tracked_files: List[str],
    tracked_filestamps: Dict[str, float],
) -> type[MyHttpRequestHandler]:
    """
    Creates a custom HTTP request handler class with reload functionality.

    Args:
    - root_path (str): The root directory path to monitor.
    - public_dir (str): The directory from which to serve public files.
    - build_handler (Callable[[], None]): The handler function to execute on build.
    - tracked_files (List[str]): The files the server is tracking for changes
    - tracked_filestamps (Dict[str, float]): The last modified timestamps for
    the files being tracked

    Returns:
    - type[MyHttpRequestHandler]: Custom HTTP request handler class.
    """

    class CustomHandler(MyHttpRequestHandler):
        """
        Custom HTTP request handler class with added reload and redirect functionality.
        """

        # Class variables to store tracked files and timestamps
        tracked_files = tracked_files
        tracked_filestamps = tracked_filestamps

        def __init__(self, *args, **kwargs):
            """
            Initializes the custom HTTP request handler.
            """
            self.root_path = root_path
            self.public_dir = public_dir
            self.build_handler = build_handler
            super().__init__(*args, directory=self.public_dir, **kwargs)

        def log_message(self, format, *args):
            """
            Overrides default log_message to exclude logging for /check_update requests.
            """
            if self.path != "/check_update":
                super().log_message(format, *args)

        def do_GET(self):
            """
            Handles GET requests.

            If the request path is '/check_update', performs a reload check.
            Otherwise, redirects requests for tracked files to their new location
            within the public directory.
            """
            if self.path == "/check_update":
                current_tracked_files = self.__class__.tracked_files
                current_tracked_filestamps = self.__class__.tracked_filestamps

                if is_needed_to_reload(
                    self.root_path,
                    tracked_files=current_tracked_files,
                    tracked_filestamps=current_tracked_filestamps,
                ):
                    print("Reloaded")
                    self.__class__.tracked_files, self.__class__.tracked_filestamps = (
                        get_updated_tracked_lists(self.root_path)
                    )
                    self.build_handler()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"update")
                else:
                    self.send_response(204)
                    self.end_headers()
            else:
                # Construct the requested file path within public_dir
                requested_file_path = self.translate_path(self.path) + ".html"

                # Check if the requested file path exists
                if os.path.exists(requested_file_path):
                    # Construct the redirect URL
                    redirect_url = f"http://{HOSTNAME}:{PORT}/{os.path.relpath(requested_file_path, self.public_dir)}"
                    self.send_response(301)
                    self.send_header("Location", redirect_url)
                    self.end_headers()
                else:
                    super().do_GET()

        def shutdown(self):
            """
            Stops the serve_forever loop.

            Blocks until the loop has finished. This must be called while
            serve_forever() is running in another thread, or it will
            deadlock.
            """
            self.__shutdown_request = True
            self.__is_shut_down.wait()

    return CustomHandler


def run(root_path: str, public_dir: str, build_handler: Callable[[], None]):
    """
    Runs the HTTP server with the custom request handler.

    Args:
    - root_path (str): The root directory path to monitor.
    - public_dir (str): The directory from which to serve public files.
    - build_handler (Callable[[], None]): The handler function to execute for build.
    """
    global HOSTNAME, PORT, tracked_files, tracked_filestamps

    # Initialize tracked files and timestamps
    tracked_files, tracked_filestamps = get_updated_tracked_lists(root_path)

    # Execute the build handler function
    build_handler()

    # Create TCP server with custom handler
    TCPHandler = create_handler(
        root_path=root_path,
        public_dir=public_dir,
        build_handler=build_handler,
        tracked_files=tracked_files,
        tracked_filestamps=tracked_filestamps,
    )

    # Start TCP server
    with socketserver.TCPServer(
        (HOSTNAME, PORT), TCPHandler, bind_and_activate=False
    ) as httpd:
        httpd.allow_reuse_address = True
        httpd.server_bind()
        httpd.server_activate()
        print("Serving at http://{}:{}".format(HOSTNAME, PORT))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down the server")
            httpd.shutdown()
