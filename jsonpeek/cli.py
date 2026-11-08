import argparse
import json
import sys

from .core import describe, render


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="jsonpeek", description="Show the structure of a JSON file.")
    ap.add_argument("file", nargs="?", help="JSON file (default: stdin)")
    ap.add_argument("--max-depth", type=int, default=8, help="nesting depth to expand (default 8)")
    args = ap.parse_args(argv)

    try:
        if args.file and args.file != "-":
            with open(args.file, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except OSError as e:
        print(f"jsonpeek: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"jsonpeek: invalid JSON: {e}", file=sys.stderr)
        return 2

    print(render(describe(data), max_depth=args.max_depth))
    return 0


if __name__ == "__main__":
    sys.exit(main())
