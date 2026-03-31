import sys

from pydantic import BaseModel

from edh_utils.scryfall import search


class CardPrinting(BaseModel):
    collector_number: str
    price_usd: str | None
    name: str


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


def fetch_card_printings(card_names: list[str]) -> dict[str, list[CardPrinting]]:
    """Fetch all printings of the given cards from Scryfall.

    Returns a dict mapping set codes to lists of CardPrinting objects,
    sorted by name within each set.
    """
    printings: dict[str, list[CardPrinting]] = {}

    for name in card_names:
        cards = search(f'!"{name}" unique:prints')
        for card in cards:
            set_code = card["set"]
            printing = CardPrinting(
                collector_number=card["collector_number"],
                price_usd=card.get("prices", {}).get("usd"),
                name=card["name"],
            )
            printings.setdefault(set_code, []).append(printing)

    for cards in printings.values():
        cards.sort(key=lambda c: c.name)

    return printings


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

    printings = fetch_card_printings(names)

    if args.output_file:
        output = open(args.output_file, "w")
    else:
        output = sys.stdout

    try:
        for set_code, cards in printings.items():
            print(f"{set_code}:", file=output)
            for card in cards:
                print(f"  {card.name} #{card.collector_number} (${card.price_usd})", file=output)
    finally:
        if args.output_file:
            output.close()
