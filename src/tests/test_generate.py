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


@unittest.skip("@@@ NEED to fix")
class TestGeneratePage(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="# Sample Title\nContent")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    def test_generate_page_success(self, mock_makedirs, mock_isfile, mock_open):
        mock_isfile.side_effect = lambda x: True

        with patch(
            "src.core.markdown_functions.markdown_to_html_node"
        ) as mock_md_to_html:
            mock_md_to_html.return_value.to_html.return_value = (
                "<h1>Sample Title</h1><p>Content</p>"
            )

            generate_page("src.md", "template.html", "dest.html")

            mock_open.assert_has_calls(
                [
                    call("src.md", "r"),
                    call("template.html", "r"),
                    call("dest.html", "w"),
                ],
                any_order=True,
            )

    @patch("os.path.isfile")
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


@unittest.skip("@@@ NEED to fix")
class TestGeneratePageRecursive(unittest.TestCase):
    @patch("os.path.isdir")
    @patch("os.path.isfile")
    @patch("os.makedirs")
    @patch("os.listdir")
    def test_generate_page_recursive(
        self, mock_listdir, mock_makedirs, mock_isfile, mock_isdir
    ):
        mock_isdir.side_effect = lambda x: x in ["content", "content/subdir"]
        mock_isfile.side_effect = lambda x: x in [
            "content/file1.md",
            "content/subdir/file2.md",
        ]
        mock_listdir.side_effect = (
            lambda x: ["file1.md"] if x == "content" else ["file2.md"]
        )

        with patch("src.core.generate.generate_page") as mock_generate_page:
            generate_page_recursive("content", "template.html", "dest")

            mock_generate_page.assert_has_calls(
                [
                    call("content/file1.md", "template.html", "dest/file1.html"),
                    call(
                        "content/subdir/file2.md",
                        "template.html",
                        "dest/subdir/file2.html",
                    ),
                ],
                any_order=True,
            )

    @patch("os.path.isdir")
    def test_generate_page_recursive_content_dir_not_found(self, mock_isdir):
        mock_isdir.side_effect = lambda x: x == "template.html"
        with self.assertRaises(FileNotFoundError):
            generate_page_recursive("non_existent_content", "template.html", "dest")

    @patch("os.path.isfile")
    def test_generate_page_recursive_template_file_not_found(self, mock_isfile):
        mock_isfile.side_effect = lambda x: x == "content"
        with self.assertRaises(FileNotFoundError):
            generate_page_recursive("content", "non_existent_template.html", "dest")


if __name__ == "__main__":
    unittest.main()
