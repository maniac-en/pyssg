import os
import shutil
import unittest
from unittest.mock import patch, call

from src.core.utils import copy_static_to_public, copy_files_rec


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
        mock_os.assert_has_calls([call.path.exists(public_dir), call.mkdir(public_dir)])
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


if __name__ == "__main__":
    unittest.main()
