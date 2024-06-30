import unittest
import os
from unittest.mock import patch, mock_open, call

from src.core.generate import extract_title, generate_page, generate_page_recursive


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
    @patch("src.core.generate.os.path.isfile")
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

    @patch("src.core.generate.open", new_callable=mock_open)
    @patch("src.core.generate.os")
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

    @patch("src.core.generate.os.path.isdir")
    def test_generate_page_recursive_content_dir_not_found(self, mock_isdir):
        mock_isdir.side_effect = lambda x: x == "template.html"
        with self.assertRaises(FileNotFoundError):
            generate_page_recursive("non_existent_content", "template.html", "dest")

    @patch("src.core.generate.os.path.isfile")
    def test_generate_page_recursive_template_file_not_found(self, mock_isfile):
        mock_isfile.side_effect = lambda x: x == "content"
        with self.assertRaises(FileNotFoundError):
            generate_page_recursive("content", "non_existent_template.html", "dest")

    @patch("src.core.generate.os")
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
        with patch("src.core.generate.generate_page") as mock_generate_page:
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


if __name__ == "__main__":
    unittest.main()
