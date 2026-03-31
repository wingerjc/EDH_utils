import csv
import enum
import io
import json
import sys

from pydantic import BaseModel

from edh_utils.scryfall import search


class OutputFormat(str, enum.Enum):
    TEXT = "text"
    JSON = "json"
    CSV = "csv"
    MD = "md"

    def __str__(self) -> str:
        return self.value


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


def _format_text(printings: dict[str, list[CardPrinting]], output: io.IOBase) -> None:
    for set_code, cards in printings.items():
        print(f"{set_code}:", file=output)
        for card in cards:
            print(f"  {card.name} #{card.collector_number} (${card.price_usd})", file=output)


def _format_json(printings: dict[str, list[CardPrinting]], output: io.IOBase) -> None:
    data = {
        set_code: [card.model_dump() for card in cards]
        for set_code, cards in printings.items()
    }
    print(json.dumps(data, indent=2), file=output)


def _format_csv(printings: dict[str, list[CardPrinting]], output: io.IOBase) -> None:
    writer = csv.writer(output)
    writer.writerow(["set", "collector_number", "name", "price_usd"])
    for set_code, cards in printings.items():
        for card in cards:
            writer.writerow([set_code, card.collector_number, card.name, card.price_usd])


def _format_md(printings: dict[str, list[CardPrinting]], output: io.IOBase) -> None:
    for set_code, cards in printings.items():
        print(f"* {set_code}", file=output)
        for card in cards:
            print(f"  * {card.name}, {card.collector_number}, {card.price_usd}", file=output)


_FORMATTERS = {
    OutputFormat.TEXT: _format_text,
    OutputFormat.JSON: _format_json,
    OutputFormat.CSV: _format_csv,
    OutputFormat.MD: _format_md,
}


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

    if args.hide:
        hidden = {code.strip() for code in args.hide.split(",")}
        printings = {k: v for k, v in printings.items() if k not in hidden}

    if args.output_file:
        output = open(args.output_file, "w")
    else:
        output = sys.stdout

    try:
        _FORMATTERS[args.format](printings, output)
    finally:
        if args.output_file:
            output.close()
