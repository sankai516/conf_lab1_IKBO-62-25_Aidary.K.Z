"""Shell emulator prototype for configuration management lab 1."""

import argparse
import os
import re
import shlex
import sys
from pathlib import Path


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


def handle_stub(cmd_name: str, args: list[str]) -> bool:
    """Handle stub command printing name and args."""
    args_repr = " ".join(args)
    if args_repr:
        print(f"stub: {cmd_name} called with args: {args_repr}")
    else:
        print(f"stub: {cmd_name} called with no args")
    return True


def execute_command(cmd: str, args: list[str]) -> tuple[bool, bool]:
    """Execute single command line token set.

    Returns tuple of (should_continue, success_status).
    """
    if cmd == "exit":
        if args:
            print("exit: too many arguments", file=sys.stderr)
            return True, False
        return False, True

    if cmd in ("ls", "cd"):
        return True, handle_stub(cmd, args)

    print(f"{cmd}: command not found", file=sys.stderr)
    return True, False


def run_repl(vfs_name: str = "vfs") -> None:
    """Run interactive CLI read-eval-print loop."""
    prompt = f"[{vfs_name}]$ "
    while True:
        try:
            line = input(prompt)
        except EOFError:
            break

        tokens = parse_input(line)
        if not tokens:
            continue

        should_continue, _ = execute_command(tokens[0], tokens[1:])
        if not should_continue:
            break


def run_script(script_path: str, vfs_name: str = "vfs") -> bool:
    """Execute commands from script file stopping on first error."""
    path = Path(script_path)
    if not path.is_file():
        print(f"script: file not found: {script_path}", file=sys.stderr)
        return False

    prompt = f"[{vfs_name}]$ "
    with path.open("r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            print(f"{prompt}{stripped}")
            tokens = parse_input(stripped)
            if not tokens:
                continue

            should_continue, ok = execute_command(tokens[0], tokens[1:])
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

    vfs_name = Path(args.vfs).name if args.vfs else "vfs"

    if args.script:
        success = run_script(args.script, vfs_name=vfs_name)
        if not success:
            sys.exit(1)
    else:
        run_repl(vfs_name=vfs_name)


if __name__ == "__main__":
    main()