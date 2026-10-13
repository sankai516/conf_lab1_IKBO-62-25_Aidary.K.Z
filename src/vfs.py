"""In-memory Virtual File System (VFS) loaded from JSON."""

import base64
import copy
import json
from pathlib import Path
from typing import Any


class VfsError(Exception):
    """Exception raised for errors in VFS operations."""


class VFS:
    """In-memory tree representing virtual file system."""

    def __init__(self, root_data: dict[str, Any]) -> None:
        """Initialize VFS instance with validated root dictionary."""
        self._root = root_data
        self._cwd_parts: list[str] = []

    @classmethod
    def load_from_json(cls, file_path: str) -> "VFS":
        """Load and parse VFS structure from a JSON file."""
        path = Path(file_path)
        if not path.is_file():
            raise VfsError(f"VFS file not found: {file_path}")

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as exc:
            raise VfsError(f"Failed to parse VFS JSON: {exc}") from exc

        if not isinstance(data, dict) or data.get("type") != "dir":
            raise VfsError("VFS root node must be a directory")

        return cls(data)

    def get_cwd_path(self) -> str:
        """Return absolute string path of current working directory."""
        if not self._cwd_parts:
            return "/"
        return "/" + "/".join(self._cwd_parts)

    def _resolve_parts(self, target_path: str) -> list[str]:
        """Resolve string path relative to cwd into canonical parts."""
        if target_path.startswith("/"):
            raw_parts = target_path.strip("/").split("/")
            parts: list[str] = []
        else:
            raw_parts = target_path.split("/")
            parts = list(self._cwd_parts)

        for part in raw_parts:
            if not part or part == ".":
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return parts

    def _get_node(self, parts: list[str]) -> dict[str, Any] | None:
        """Traverse tree by path components and return dictionary node."""
        curr = self._root
        for part in parts:
            if curr.get("type") != "dir":
                return None
            children = curr.get("children", {})
            if part not in children:
                return None
            curr = children[part]
        return curr

    def change_dir(self, target_path: str) -> None:
        """Change current directory to resolved target path."""
        parts = self._resolve_parts(target_path)
        node = self._get_node(parts)
        if node is None:
            raise VfsError(f"cd: no such file or directory: {target_path}")
        if node.get("type") != "dir":
            raise VfsError(f"cd: not a directory: {target_path}")
        self._cwd_parts = parts

    def list_dir(self, target_path: str | None = None) -> list[str]:
        """List file and folder names inside specified or current dir."""
        parts = (
            self._resolve_parts(target_path)
            if target_path
            else self._cwd_parts
        )
        node = self._get_node(parts)
        if node is None:
            raise VfsError(f"ls: cannot access '{target_path}': No such entry")
        if node.get("type") != "dir":
            return [parts[-1]] if parts else []
        children = node.get("children", {})
        return sorted(list(children.keys()))

    def get_owner(self, target_path: str) -> str:
        """Get owner property of the specified node."""
        parts = self._resolve_parts(target_path)
        node = self._get_node(parts)
        if node is None:
            raise VfsError(f"No such file or directory: {target_path}")
        return node.get("owner", "root")

    def change_owner(self, new_owner: str, target_path: str) -> None:
        """Change owner of specified file or directory."""
        parts = self._resolve_parts(target_path)
        node = self._get_node(parts)
        if node is None:
            raise VfsError(f"chown: cannot access '{target_path}': No such entry")
        node["owner"] = new_owner

    def copy_node(self, src_path: str, dst_path: str) -> None:
        """Copy file or directory from src to dst inside VFS."""
        src_parts = self._resolve_parts(src_path)
        src_node = self._get_node(src_parts)
        if src_node is None:
            raise VfsError(f"cp: cannot stat '{src_path}': No such entry")

        dst_parts = self._resolve_parts(dst_path)
        dst_node = self._get_node(dst_parts)

        if dst_node and dst_node.get("type") == "dir":
            leaf_name = src_parts[-1] if src_parts else "root_copy"
            target_parent = dst_node
            target_name = leaf_name
        else:
            if not dst_parts:
                raise VfsError("cp: cannot overwrite root")
            parent_parts = dst_parts[:-1]
            target_name = dst_parts[-1]
            target_parent = self._get_node(parent_parts)
            if target_parent is None or target_parent.get("type") != "dir":
                raise VfsError(f"cp: target parent directory not found")

        copied_data = copy.deepcopy(src_node)
        target_parent.setdefault("children", {})[target_name] = copied_data

    def get_tree_lines(self, start_path: str | None = None) -> list[str]:
        """Generate lines of directory hierarchy tree."""
        parts = (
            self._resolve_parts(start_path)
            if start_path
            else self._cwd_parts
        )
        node = self._get_node(parts)
        if node is None:
            raise VfsError("tree: target directory not found")
        if node.get("type") != "dir":
            raise VfsError("tree: target is not a directory")

        root_label = parts[-1] if parts else "."
        lines = [root_label]
        self._build_tree_recursive(node, "", lines)
        return lines

    def _build_tree_recursive(
        self, node: dict[str, Any], prefix: str, lines: list[str]
    ) -> None:
        """Helper to recursively format tree branches."""
        children = node.get("children", {})
        names = sorted(list(children.keys()))
        total = len(names)
        for idx, name in enumerate(names):
            is_last = idx == total - 1
            branch = "└── " if is_last else "├── "
            lines.append(f"{prefix}{branch}{name}")
            child = children[name]
            if child.get("type") == "dir":
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._build_tree_recursive(child, next_prefix, lines)