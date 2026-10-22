"""In-memory Virtual File System (VFS) loaded from JSON."""

import base64
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

    def read_file_text(self, file_path: str) -> str:
        """Read and decode base64 text content from specified file."""
        parts = self._resolve_parts(file_path)
        node = self._get_node(parts)
        if node is None:
            raise VfsError(f"cat: {file_path}: No such file")
        if node.get("type") != "file":
            raise VfsError(f"cat: {file_path}: Is a directory")

        raw_b64 = node.get("content", "")
        try:
            return base64.b64decode(raw_b64).decode("utf-8")
        except Exception as exc:
            raise VfsError(
                f"cat: corrupted base64 data in {file_path}"
            ) from exc