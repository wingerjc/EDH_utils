import argparse

from edh_utils.set_finder import set_finder
from edh_utils.set_finder.set_finder import OutputFormat


def main():
    parser = argparse.ArgumentParser(prog="edh-utils")
    subparsers = parser.add_subparsers(dest="command", required=True)

    set_finder_parser = subparsers.add_parser("set-finder")
    set_finder_parser.add_argument(
        "-f", "--file", metavar="FILE", help="Input file (default: stdin)"
    )
    set_finder_parser.add_argument(
        "-o", "--output-file", metavar="FILE", help="Output file (default: stdout)"
    )
    set_finder_parser.add_argument(
        "-s", "--settings", metavar="FILE", help="TOML settings file"
    )
    set_finder_parser.add_argument(
        "-c", "--collection", metavar="FILE", help="JSON file mapping locations to set codes"
    )
    set_finder_parser.add_argument(
        "--hide",
        metavar="SETS",
        default=None,
        help="Comma-separated list of set codes to exclude from output",
    )
    set_finder_parser.add_argument(
        "--format",
        choices=list(OutputFormat),
        default=None,
        type=OutputFormat,
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.command == "set-finder":
        set_finder(args)


if __name__ == "__main__":
    main()
