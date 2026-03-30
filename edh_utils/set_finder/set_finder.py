import sys


def read_card_names(source) -> list[str]:
    """Parse card names from a file-like object.

    Each line should be in the format '<count> <name>' or '<name>'.
    Returns a sorted, de-duped list of card names.
    """
    names = set()
    for line in source:
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            names.add(parts[1].strip())
        else:
            names.add(line)
    return sorted(names)


def set_finder(args):
    """Find and display all sets containing each card in the input list.

    Reads card names from a file (-f/--file) or stdin, then for each unique
    card prints the sets it appears in — making it easy to identify which
    sets can supply every card needed for a deck or cube.
    """
    if args.file:
        with open(args.file) as f:
            names = read_card_names(f)
    else:
        names = read_card_names(sys.stdin)
    for name in names:
        print(name)
