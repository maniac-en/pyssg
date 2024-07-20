import os
import unittest
from unittest.mock import patch, call, mock_open

from src.core.utils import (
    copy_files_rec,
    copy_static_to_public,
    extract_title,
    generate_page,
    generate_page_recursive,
    build_site,
)


class TestCopyStaticToPublic(unittest.TestCase):
    @patch("src.core.utils.copy_files_rec")
    @patch("src.core.utils.shutil")
    @patch("src.core.utils.os")
    def test_copy_static_to_public(self, mock_os, mock_shutil, mock_copy_files_rec):
        static_dir = os.path.join("src", "static")
        public_dir = "public"

        # Setup mock
        mock_os.path.exists.return_value = True

        # Run the function
        copy_static_to_public(static_dir, public_dir)

        # Assert calls
        mock_os.assert_has_calls(
            [call.path.exists(public_dir), call.mkdir(public_dir)], any_order=True
        )
        mock_shutil.rmtree.assert_called_once_with(public_dir)
        mock_copy_files_rec.assert_called_once_with(static_dir, public_dir)

    @patch("src.core.utils.copy_files_rec")
    @patch("src.core.utils.shutil")
    @patch("src.core.utils.os")
    def test_copy_static_to_public_no_existing_public(
        self, mock_os, mock_shutil, mock_copy_files_rec
    ):
        static_dir = "src/static"
        public_dir = "public"

        # Setup mock
        mock_os.path.exists.return_value = False

        # Run the function
        copy_static_to_public(static_dir, public_dir)

        # Assert calls
        mock_os.path.exists.assert_called_once_with(public_dir)
        self.assertFalse(mock_shutil.rmtree.called)
        mock_os.mkdir.assert_called_once_with(public_dir)
        mock_copy_files_rec.assert_called_once_with(static_dir, public_dir)


class TestCopyFilesRec(unittest.TestCase):
    @patch("src.core.utils.os.path.exists")
    def test_copy_files_rec_source_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            copy_files_rec("a", "b")

    @patch("src.core.utils.os.listdir")
    @patch("src.core.utils.os.makedirs")
    @patch("src.core.utils.os.path.exists")
    def test_copy_files_rec_destination_not_exists(
        self, mock_exists, mock_makedirs, mock_listdir
    ):
        mock_exists.side_effect = lambda x: False if x != "a" else True
        mock_listdir.return_value = []  # do not enter the for loop

        copy_files_rec("a", "b")

        mock_makedirs.assert_called_once_with("b", exist_ok=True)

    @patch("src.core.utils.os.listdir")
    @patch("src.core.utils.os.makedirs")
    @patch("src.core.utils.os.path.exists")
    def test_copy_files_rec_destination_exists(
        self, mock_exists, mock_makedirs, mock_listdir
    ):
        mock_exists.return_value = True
        mock_listdir.return_value = []  # do not enter the for loop

        copy_files_rec("a", "b")

        self.assertFalse(mock_makedirs.called)

    @patch("src.core.utils.shutil")
    @patch("src.core.utils.os")
    def test_copy_files_rec_success(self, mock_os, mock_shutil):
        # Setup mock for os.path.exists
        def path_exists_side_effect(path):
            if path == "a":
                return True
            if path == "b":
                return False
            if path == os.path.join("a", "subdir"):
                return True
            if path == os.path.join("b", "subdir"):
                return False
            return False

        mock_os.path.exists.side_effect = path_exists_side_effect

        # Setup mock for os.path.isfile
        def is_file_side_effect(path):
            if path == os.path.join("a", "file1.txt"):
                return True
            if path == os.path.join("a", "subdir"):
                return False
            if path == os.path.join("a", "subdir", "file2.txt"):
                return True
            return False

        mock_os.path.isfile.side_effect = is_file_side_effect

        # Setup mock for os.path.isdir
        def is_dir_side_effect(path):
            if path == os.path.join("a", "subdir"):
                return True
            return False

        mock_os.path.isdir.side_effect = is_dir_side_effect

        # Setup mock for os.listdir
        def listdir_side_effect(path):
            if path == "a":
                return ["file1.txt", "subdir"]
            if path == os.path.join("a", "subdir"):
                return ["file2.txt"]
            return []

        mock_os.listdir.side_effect = listdir_side_effect

        # Setup mock for os.path.join
        def join_side_effect(a, b):
            return f"{a}/{b}"

        mock_os.path.join.side_effect = join_side_effect

        # Run the function
        copy_files_rec("a", "b")

        # Assert calls
        expected_os_calls = [
            call.path.exists("a"),
            call.path.exists("b"),
            call.makedirs("b", exist_ok=True),
            call.listdir("a"),
            call.path.join("a", "file1.txt"),
            call.path.join("b", "file1.txt"),
            call.path.isfile("a/file1.txt"),
            call.path.join("a", "subdir"),
            call.path.join("b", "subdir"),
            call.path.isfile("a/subdir"),
            call.path.isdir("a/subdir"),
            call.path.exists("b/subdir"),
            call.mkdir("b/subdir"),
            call.path.exists("a/subdir"),
            call.path.exists("b/subdir"),
            call.makedirs("b/subdir", exist_ok=True),
            call.listdir("a/subdir"),
            call.path.join("a/subdir", "file2.txt"),
            call.path.join("b/subdir", "file2.txt"),
            call.path.isfile("a/subdir/file2.txt"),
        ]

        mock_os.assert_has_calls(expected_os_calls, any_order=True)

        expected_shutil_calls = [
            call.copy(
                src=os.path.join("a", "file1.txt"),
                dst=os.path.join("b", "file1.txt"),
            ),
            call.copy(
                src=os.path.join("a", "subdir", "file2.txt"),
                dst=os.path.join("b", "subdir", "file2.txt"),
            ),
        ]

        mock_shutil.assert_has_calls(expected_shutil_calls, any_order=True)


class TestExtractTitle(unittest.TestCase):
    def test_single_h1_header(self):
        text = "# This is a title"
        self.assertEqual(extract_title(text), "This is a title")

    def test_multiple_headers(self):
        text = """\
# First Title
Some content here.
# Second Title
## Subheader\
        """
        self.assertEqual(extract_title(text), "First Title")

    def test_no_h1_header(self):
        text = """\
## This is a subheader
Some content here.
### Another subheader
        """
        with self.assertRaises(ValueError):
            extract_title(text)

    def test_h1_header_with_special_characters(self):
        text = "# Title with special characters !@#$%^&*()"
        self.assertEqual(
            extract_title(text), "Title with special characters !@#$%^&*()"
        )

    def test_h1_header_with_leading_and_trailing_spaces(self):
        text = "#    Title with leading and trailing spaces    "
        self.assertEqual(
            extract_title(text.strip()), "Title with leading and trailing spaces"
        )


class TestGeneratePage(unittest.TestCase):
    @patch("src.core.utils.os.path.isfile")
    def test_generate_page_source_file_not_found(self, mock_isfile):
        mock_isfile.side_effect = lambda x: x == "template.html"
        with self.assertRaises(FileNotFoundError):
            generate_page("non_existent_src.md", "template.html", "dest.html")

    @patch("os.path.isfile")
    def test_generate_page_template_file_not_found(self, mock_isfile):
        mock_isfile.side_effect = lambda x: x == "src.md"
        with self.assertRaises(FileNotFoundError):
            generate_page("src.md", "non_existent_template.html", "dest.html")

    @patch(
        "builtins.open", new_callable=mock_open, read_data="## No h1 header\nContent"
    )
    @patch("os.path.isfile")
    def test_generate_page_no_h1_header(self, mock_isfile, mock_open):
        mock_isfile.side_effect = lambda x: True
        with self.assertRaises(ValueError):
            generate_page("src.md", "template.html", "dest.html")

    @patch("src.core.utils.open", new_callable=mock_open)
    @patch("src.core.utils.os")
    def test_generate_page_success(self, mock_os, mock_file_open):
        # Setup Mock
        mock_os.path.isfile.side_effect = lambda x: True
        mock_os.path.dirname.return_value = "dir"
        mock_os.path.exists.return_value = False
        mock_file_a = mock_open(read_data="# Sample Title\nContent").return_value
        mock_file_b = mock_open(
            read_data="<html><head><title>{{ Title }}</title></head><body>{{ Content }}</body></html>"
        ).return_value
        mock_file_c = mock_open().return_value
        expected_output = "<html><head><title>Sample Title</title></head><body><div><h1>Sample Title\nContent</h1></div></body></html>"

        # Configure mock to return the mock file handles in order
        mock_file_open.side_effect = [mock_file_a, mock_file_b, mock_file_c]

        # Run function
        generate_page("src.md", "template.html", "dest.html")

        # Assert calls
        mock_os.path.isfile.assert_has_calls([call("src.md"), call("template.html")])
        mock_file_open.assert_any_call("src.md", "r")
        mock_file_a.read.assert_called_once()
        mock_file_open.assert_any_call("template.html", "r")
        mock_file_b.read.assert_called_once()
        mock_os.path.dirname.assert_any_call("dest.html")
        mock_os.path.exists.assert_any_call("dir")
        mock_os.makedirs.assert_any_call("dir")
        mock_file_open.assert_any_call("dest.html", "w")
        mock_file_c.write.assert_called_once_with(expected_output)

    @patch("src.core.utils.os.path.isdir")
    def test_generate_page_recursive_content_dir_not_found(self, mock_isdir):
        mock_isdir.side_effect = lambda x: x == "template.html"
        with self.assertRaises(FileNotFoundError):
            generate_page_recursive("non_existent_content", "template.html", "dest")

    @patch("src.core.utils.os.path.isfile")
    def test_generate_page_recursive_template_file_not_found(self, mock_isfile):
        mock_isfile.side_effect = lambda x: x == "content"
        with self.assertRaises(FileNotFoundError):
            generate_page_recursive("content", "non_existent_template.html", "dest")

    @patch("src.core.utils.os")
    def test_generate_page_recursive(self, mock_os):
        # Setup mock for os.path.isfile
        def is_file_side_effect(file_path):
            if file_path == "template.html":
                return True
            if file_path == os.path.join("content", "file1.md"):
                return True
            if file_path == os.path.join("content", "subdir"):
                return False
            if file_path == os.path.join("content", "subdir", "file2.md"):
                return True
            return False

        mock_os.path.isfile.side_effect = is_file_side_effect

        # Setup mock for os.path.isdir
        def is_dir_side_effect(path):
            if path == "content":
                return True
            if path == os.path.join("content", "subdir"):
                return True
            return False

        mock_os.path.isdir.side_effect = is_dir_side_effect

        # Setup mock for os.listdir
        def listdir_side_effect(path):
            if path == "content":
                return ["file1.md", "subdir"]
            if path == os.path.join("content", "subdir"):
                return ["file2.md"]
            return []

        mock_os.listdir.side_effect = listdir_side_effect

        # Setup mock for os.path.join
        def join_side_effect(a, b):
            return f"{a}/{b}"

        mock_os.path.join.side_effect = join_side_effect

        # Assert calls
        with patch("src.core.utils.generate_page") as mock_generate_page:
            generate_page_recursive("content", "template.html", "dest")

            expected_os_calls = [
                call.path.isdir("content"),
                call.path.isfile("template.html"),
                call.listdir("content"),
                call.path.join("content", "file1.md"),
                call.path.join("dest", "file1.md"),
                call.path.isfile("content/file1.md"),
                call.path.join("content", "subdir"),
                call.path.join("dest", "subdir"),
                call.path.isfile("content/subdir"),
                call.path.isdir("content/subdir"),
                call.path.join("dest", "subdir"),
                call.makedirs("dest/subdir", exist_ok=True),
                call.path.isdir("content/subdir"),
                call.path.isfile("template.html"),
                call.listdir("content/subdir"),
                call.path.join("content/subdir", "file2.md"),
                call.path.join("dest/subdir", "file2.md"),
                call.path.isfile("content/subdir/file2.md"),
            ]
            mock_os.assert_has_calls(expected_os_calls)

            mock_generate_page.assert_has_calls(
                [
                    call("content/file1.md", "template.html", "dest/file1.html"),
                    call(
                        "content/subdir/file2.md",
                        "template.html",
                        "dest/subdir/file2.html",
                    ),
                ],
            )


class TestBuildSite(unittest.TestCase):
    def setUp(self):
        self.static_dir = "test_static"
        self.content_dir = "test_content"
        self.template_path = "test_template.html"
        self.dest_path = "test_output"

        # Create test directories and files
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(self.content_dir, exist_ok=True)
        with open(self.template_path, "w") as f:
            f.write(
                "<html><head><title>{{ Title }}</title></head><body>{{ Content }}</body></html>"
            )
        with open(os.path.join(self.content_dir, "test.md"), "w") as f:
            f.write("# Test Page\nThis is a test.")
        with open(os.path.join(self.static_dir, "style.css"), "w") as f:
            f.write("body { font-family: Arial; }")

    def tearDown(self):
        # Clean up test directories and files
        for dir_path in [self.static_dir, self.content_dir, self.dest_path]:
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(dir_path)
        if os.path.exists(self.template_path):
            os.remove(self.template_path)

    @patch(
        "src.core.utils.os.path.isdir", side_effect=lambda x: x != "invalid_content_dir"
    )
    @patch("src.core.utils.os.path.isfile", return_value=True)
    @patch("src.core.utils.copy_static_to_public")
    def test_build_site_content_dir_not_found(
        self, mock_copy_static, mock_isfile, mock_isdir
    ):
        with self.assertRaises(FileNotFoundError):
            build_function = build_site(
                self.static_dir,
                "invalid_content_dir",
                self.template_path,
                self.dest_path,
            )
            build_function()

    @patch("src.core.utils.os.path.isdir", return_value=True)
    @patch(
        "src.core.utils.os.path.isfile",
        side_effect=lambda x: x != "invalid_template.html",
    )
    @patch("src.core.utils.copy_static_to_public")
    def test_build_site_template_file_not_found(
        self, mock_copy_static, mock_isfile, mock_isdir
    ):
        with self.assertRaises(FileNotFoundError):
            build_function = build_site(
                self.static_dir,
                self.content_dir,
                "invalid_template.html",
                self.dest_path,
            )
            build_function()

    @patch("src.core.utils.generate_page_recursive")
    @patch("src.core.utils.copy_static_to_public")
    def test_build_site_closure(self, mock_copy_static, mock_generate_page_recursive):
        build_function = build_site(
            self.static_dir, self.content_dir, self.template_path, self.dest_path
        )

        # Check if the returned object is callable
        self.assertTrue(callable(build_function))

        # Call the closure and check if generate_page_recursive was called
        build_function()
        mock_generate_page_recursive.assert_called_once_with(
            content_dir=self.content_dir,
            template_path=self.template_path,
            dest_path=self.dest_path,
        )
        mock_copy_static.assert_called_once_with(
            static_dir=self.static_dir, public_dir=self.dest_path
        )

    @patch("builtins.print")
    @patch("src.core.utils.os.makedirs")
    @patch("src.core.utils.os.path.isdir", return_value=True)
    @patch("src.core.utils.os.path.isfile", return_value=True)
    @patch("src.core.utils.generate_page_recursive")
    @patch("src.core.utils.copy_static_to_public")
    def test_build_site_success(
        self,
        mock_copy_static,
        mock_generate_page_recursive,
        mock_isfile,
        mock_isdir,
        mock_makedirs,
        mock_print,
    ):
        build_function = build_site(
            self.static_dir, self.content_dir, self.template_path, self.dest_path
        )
        build_function()

        mock_copy_static.assert_called_once_with(
            static_dir=self.static_dir, public_dir=self.dest_path
        )
        mock_generate_page_recursive.assert_called_once_with(
            content_dir=self.content_dir,
            template_path=self.template_path,
            dest_path=self.dest_path,
        )


if __name__ == "__main__":
    unittest.main()
