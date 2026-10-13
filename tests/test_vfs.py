"""Unit tests for Virtual File System operations."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vfs import VFS, VfsError


class TestVfsOperations(unittest.TestCase):
    """Test suite covering ls, cd, cp, chown, tree in VFS."""

    def setUp(self) -> None:
        """Create fresh in-memory VFS structure for each test."""
        raw_vfs = {
            "type": "dir",
            "owner": "root",
            "children": {
                "folder1": {
                    "type": "dir",
                    "owner": "root",
                    "children": {
                        "file1.txt": {
                            "type": "file",
                            "owner": "root",
                            "content": "dGVzdA==",
                        }
                    },
                },
                "root_file.txt": {
                    "type": "file",
                    "owner": "root",
                    "content": "cm9vdA==",
                },
            },
        }
        self.vfs = VFS(raw_vfs)

    def test_list_dir(self) -> None:
        """Test listing directory contents."""
        items = self.vfs.list_dir()
        self.assertEqual(items, ["folder1", "root_file.txt"])

    def test_change_dir_and_cwd(self) -> None:
        """Test directory navigation and path resolution."""
        self.vfs.change_dir("folder1")
        self.assertEqual(self.vfs.get_cwd_path(), "/folder1")
        self.assertEqual(self.vfs.list_dir(), ["file1.txt"])
        self.vfs.change_dir("..")
        self.assertEqual(self.vfs.get_cwd_path(), "/")

    def test_change_dir_invalid(self) -> None:
        """Test changing to non-existent directory raises error."""
        with self.assertRaises(VfsError):
            self.vfs.change_dir("non_existent")

    def test_copy_file(self) -> None:
        """Test copying file inside VFS."""
        self.vfs.copy_node("root_file.txt", "copy.txt")
        items = self.vfs.list_dir()
        self.assertIn("copy.txt", items)

    def test_copy_directory_recursive(self) -> None:
        """Test deep copy of a directory."""
        self.vfs.copy_node("folder1", "folder2")
        self.assertIn("folder2", self.vfs.list_dir())
        self.assertEqual(self.vfs.list_dir("folder2"), ["file1.txt"])

    def test_change_owner(self) -> None:
        """Test modifying owner attribute."""
        self.vfs.change_owner("developer", "root_file.txt")
        self.assertEqual(self.vfs.get_owner("root_file.txt"), "developer")

    def test_tree_generation(self) -> None:
        """Test recursive tree lines format."""
        tree_lines = self.vfs.get_tree_lines()
        self.assertEqual(tree_lines[0], ".")
        self.assertTrue(any("folder1" in line for line in tree_lines))
        self.assertTrue(any("file1.txt" in line for line in tree_lines))


if __name__ == "__main__":
    unittest.main()