import os
import shutil
import unittest
from unittest.mock import patch, call

from src.main import copy_static_to_public


@unittest.skip("@@@ NEED to fix")
class TestCopyStaticToPublic(unittest.TestCase):
    @patch("os.path.exists")
    @patch("shutil.rmtree")
    @patch("os.mkdir")
    @patch("os.listdir")
    @patch("shutil.copy")
    def test_copy_static_to_public(
        self, mock_copy, mock_listdir, mock_mkdir, mock_rmtree, mock_exists
    ):
        static_dir = "static"
        public_dir = "public"

        # Setup mock
        mock_exists.side_effect = lambda x: x == public_dir
        mock_listdir.side_effect = [
            ["file1.txt", "subdir"],  # Files in static_dir
            ["file2.txt"],  # Files in static/subdir
        ]

        # Run the function
        copy_static_to_public(static_dir, public_dir)

        # Assert calls
        mock_exists.assert_called_with(public_dir)
        mock_rmtree.assert_called_once_with(public_dir)
        mock_mkdir.assert_has_calls([call(public_dir), call(f"{public_dir}/subdir")])
        mock_copy.assert_has_calls(
            [
                call(src=f"{static_dir}/file1.txt", dst=f"{public_dir}/file1.txt"),
                call(
                    src=f"{static_dir}/subdir/file2.txt",
                    dst=f"{public_dir}/subdir/file2.txt",
                ),
            ]
        )

    @patch("os.path.exists")
    @patch("os.mkdir")
    @patch("os.listdir")
    @patch("shutil.copy")
    def test_copy_static_to_public_no_existing_public(
        self, mock_copy, mock_listdir, mock_mkdir, mock_exists
    ):
        static_dir = "static"
        public_dir = "public"

        # Setup mock
        mock_exists.side_effect = lambda x: x == public_dir
        mock_listdir.side_effect = [
            ["file1.txt", "subdir"],  # Files in static_dir
            ["file2.txt"],  # Files in static/subdir
        ]
        mock_exists.return_value = False

        # Run the function
        copy_static_to_public(static_dir, public_dir)

        # Assert calls
        mock_exists.assert_called_with(public_dir)
        mock_mkdir.assert_has_calls([call(public_dir), call(f"{public_dir}/subdir")])
        mock_copy.assert_has_calls(
            [
                call(src=f"{static_dir}/file1.txt", dst=f"{public_dir}/file1.txt"),
                call(
                    src=f"{static_dir}/subdir/file2.txt",
                    dst=f"{public_dir}/subdir/file2.txt",
                ),
            ]
        )


if __name__ == "__main__":
    unittest.main()
