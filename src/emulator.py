"""Shell emulator prototype for configuration management lab 1."""

import os
import re
import shlex
import sys


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


def handle_stub(cmd_name: str, args: list[str]) -> None:
    """Handle stub command printing name and args."""
    args_repr = " ".join(args)
    if args_repr:
        print(f"stub: {cmd_name} called with args: {args_repr}")
    else:
        print(f"stub: {cmd_name} called with no args")


def execute_command(cmd: str, args: list[str]) -> bool:
    """Execute single command line token set.

    Return False to stop the shell loop, True to continue.
    """
    if cmd == "exit":
        if args:
            print("exit: too many arguments", file=sys.stderr)
            return True
        return False

    if cmd in ("ls", "cd"):
        handle_stub(cmd, args)
        return True

    print(f"{cmd}: command not found", file=sys.stderr)
    return True


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

        cmd = tokens[0]
        args = tokens[1:]
        should_continue = execute_command(cmd, args)
        if not should_continue:
            break


def main() -> None:
    """Entry point for CLI emulator."""
    run_repl()


if __name__ == "__main__":
    main()