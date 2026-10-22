"""Shell emulator prototype for configuration management lab 1."""

import argparse
import os
import re
import shlex
import sys
from pathlib import Path
REQUIRED_TWO_ARGS: int = 2

from vfs import VFS, VfsError


def expand_env_vars(raw_line: str) -> str:
    """Expand real OS environment variables in raw line."""
    pattern = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")

    def replace_match(match: re.Match) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, "")

    return pattern.sub(replace_match, raw_line)


def parse_input(raw_line: str) -> list[str]:
    """Parse shell line with environment expansion."""
    expanded_line = expand_env_vars(raw_line.strip())
    if not expanded_line:
        return []
    return shlex.split(expanded_line)


def execute_command(
    cmd: str, args: list[str], vfs: VFS | None
) -> tuple[bool, bool]:
    """Execute single command line token set."""
    if cmd == "exit":
        if args:
            print("exit: too many arguments", file=sys.stderr)
            return True, False
        return False, True

    handlers = {
        "ls": handle_ls,
        "cd": handle_cd,
        "cp": handle_cp,
        "chown": handle_chown,
        "tree": handle_tree,
    }
    handler = handlers.get(cmd)
    if handler:
        return handler(args, vfs)

    print(f"{cmd}: command not found", file=sys.stderr)
    return True, False


def handle_ls(args: list[str], vfs: VFS | None) -> tuple[bool, bool]:
    """Handle ls command listing files and directories."""
    if vfs is None:
        print("ls: no VFS loaded", file=sys.stderr)
        return True, False

    target = args[0] if args else None
    try:
        entries = vfs.list_dir(target)
        for item in entries:
            print(item)
        return True, True
    except VfsError as exc:
        print(str(exc), file=sys.stderr)
        return True, False


def handle_cd(args: list[str], vfs: VFS | None) -> tuple[bool, bool]:
    """Handle cd command changing directory."""
    if vfs is None:
        print("cd: no VFS loaded", file=sys.stderr)
        return True, False

    target = "/" if not args else args[0]
    try:
        vfs.change_dir(target)
        return True, True
    except VfsError as exc:
        print(str(exc), file=sys.stderr)
        return True, False


def handle_cp(args: list[str], vfs: VFS | None) -> tuple[bool, bool]:
    """Handle cp command copying file or directory."""
    if vfs is None:
        print("cp: no VFS loaded", file=sys.stderr)
        return True, False

    if len(args) != REQUIRED_TWO_ARGS:
        print("cp: missing destination file operand", file=sys.stderr)
        return True, False

    try:
        vfs.copy_node(args[0], args[1])
        return True, True
    except VfsError as exc:
        print(str(exc), file=sys.stderr)
        return True, False


def handle_chown(args: list[str], vfs: VFS | None) -> tuple[bool, bool]:
    """Handle chown command changing node owner."""
    if vfs is None:
        print("chown: no VFS loaded", file=sys.stderr)
        return True, False

    if len(args) != REQUIRED_TWO_ARGS:
        print("chown: invalid number of arguments", file=sys.stderr)
        return True, False

    try:
        vfs.change_owner(args[0], args[1])
        return True, True
    except VfsError as exc:
        print(str(exc), file=sys.stderr)
        return True, False


def handle_tree(args: list[str], vfs: VFS | None) -> tuple[bool, bool]:
    """Handle tree command showing directory structure."""
    if vfs is None:
        print("tree: no VFS loaded", file=sys.stderr)
        return True, False

    target = args[0] if args else None
    try:
        lines = vfs.get_tree_lines(target)
        for line in lines:
            print(line)
        return True, True
    except VfsError as exc:
        print(str(exc), file=sys.stderr)
        return True, False


def get_prompt(vfs_name: str, vfs: VFS | None) -> str:
    """Format shell prompt string with current path."""
    if vfs:
        cwd = vfs.get_cwd_path()
        return f"[{vfs_name}:{cwd}]$ "
    return f"[{vfs_name}]$ "


def run_repl(vfs_name: str, vfs: VFS | None) -> None:
    """Run interactive CLI read-eval-print loop."""
    while True:
        prompt = get_prompt(vfs_name, vfs)
        try:
            line = input(prompt)
        except EOFError:
            break

        tokens = parse_input(line)
        if not tokens:
            continue

        should_continue, _ = execute_command(tokens[0], tokens[1:], vfs)
        if not should_continue:
            break


def run_script(script_path: str, vfs_name: str, vfs: VFS | None) -> bool:
    """Execute commands from script file stopping on first error."""
    path = Path(script_path)
    if not path.is_file():
        print(f"script: file not found: {script_path}", file=sys.stderr)
        return False

    with path.open("r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            prompt = get_prompt(vfs_name, vfs)
            print(f"{prompt}{stripped}")
            tokens = parse_input(stripped)
            if not tokens:
                continue

            should_continue, ok = execute_command(
                tokens[0], tokens[1:], vfs
            )
            if not ok:
                msg = f"script: error at line {line_num}: {stripped}"
                print(msg, file=sys.stderr)
                return False
            if not should_continue:
                break
    return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the emulator."""
    parser = argparse.ArgumentParser(description="CLI Shell Emulator")
    parser.add_argument("--vfs", type=str, default="", help="Path to VFS")
    parser.add_argument(
        "--script", type=str, default="", help="Path to startup script"
    )
    return parser.parse_args()


def print_debug_config(vfs_path: str, script_path: str) -> None:
    """Print debug configuration parameters."""
    print("=== Configuration Debug Info ===")
    print(f"VFS Path: {vfs_path if vfs_path else '<not specified>'}")
    print(f"Script Path: {script_path if script_path else '<not specified>'}")
    print("================================")


def main() -> None:
    """Entry point for CLI emulator."""
    args = parse_args()
    print_debug_config(args.vfs, args.script)

    vfs_instance = None
    if args.vfs:
        try:
            vfs_instance = VFS.load_from_json(args.vfs)
        except VfsError as exc:
            print(f"vfs load error: {exc}", file=sys.stderr)
            sys.exit(1)

    vfs_name = Path(args.vfs).name if args.vfs else "vfs"

    if args.script:
        success = run_script(args.script, vfs_name, vfs_instance)
        if not success:
            sys.exit(1)
    else:
        run_repl(vfs_name, vfs_instance)


if __name__ == "__main__":
    main()