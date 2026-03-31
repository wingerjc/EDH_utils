import csv
import enum
import io
import json
import sys
import tomllib

from pydantic import BaseModel

from edh_utils.scryfall import search

DEFAULT_LOCATION = "Printings"


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


def read_settings(path: str) -> dict:
    """Read a TOML settings file and return its contents as a dict.

    Supported keys: hide (list of set codes), collection (file path), format (output format).
    """
    with open(path, "rb") as f:
        return tomllib.load(f)


def read_collection(path: str) -> dict[str, list[str]]:
    """Read a collection file and invert it to set_code -> [locations].

    The file is a JSON map of location -> [set_codes].
    Returns an inverted map of set_code -> [locations].
    """
    with open(path) as f:
        data = json.load(f)
    inverted: dict[str, list[str]] = {}
    for location, set_codes in data.items():
        for set_code in set_codes:
            inverted.setdefault(set_code, []).append(location)
    return inverted


def fetch_card_printings(
    card_names: list[str],
    set_locations: dict[str, list[str]] | None = None,
) -> dict[str, dict[str, list[CardPrinting]]]:
    """Fetch all printings of the given cards from Scryfall.

    Returns a dict mapping location -> set_code -> list of CardPrinting objects,
    sorted by name within each set. Sets not found in set_locations are grouped
    under DEFAULT_LOCATION. Sets in multiple locations appear under each.
    """
    flat_printings: dict[str, list[CardPrinting]] = {}

    for name in card_names:
        cards = search(f'!"{name}" unique:prints')
        for card in cards:
            set_code = card["set"]
            printing = CardPrinting(
                collector_number=card["collector_number"],
                price_usd=card.get("prices", {}).get("usd"),
                name=card["name"],
            )
            flat_printings.setdefault(set_code, []).append(printing)

    for cards in flat_printings.values():
        cards.sort(key=lambda c: c.name)

    grouped: dict[str, dict[str, list[CardPrinting]]] = {}
    for set_code, cards in flat_printings.items():
        locations = (
            set_locations.get(set_code, [DEFAULT_LOCATION])
            if set_locations
            else [DEFAULT_LOCATION]
        )
        for location in locations:
            grouped.setdefault(location, {})[set_code] = cards

    return grouped


def _format_text(grouped: dict[str, dict[str, list[CardPrinting]]], output: io.IOBase) -> None:
    for location, printings in grouped.items():
        print(f"{location}:", file=output)
        for set_code, cards in printings.items():
            print(f"  {set_code}:", file=output)
            for card in cards:
                print(f"    {card.name} #{card.collector_number} (${card.price_usd})", file=output)


def _format_json(grouped: dict[str, dict[str, list[CardPrinting]]], output: io.IOBase) -> None:
    data = {
        location: {
            set_code: [card.model_dump() for card in cards]
            for set_code, cards in printings.items()
        }
        for location, printings in grouped.items()
    }
    print(json.dumps(data, indent=2), file=output)


def _format_csv(grouped: dict[str, dict[str, list[CardPrinting]]], output: io.IOBase) -> None:
    writer = csv.writer(output)
    writer.writerow(["set", "collector_number", "name", "price_usd", "location"])
    for location, printings in grouped.items():
        loc_display = "unknown" if location == DEFAULT_LOCATION else location
        for set_code, cards in printings.items():
            for card in cards:
                writer.writerow([set_code, card.collector_number, card.name, card.price_usd, loc_display])


def _format_md(grouped: dict[str, dict[str, list[CardPrinting]]], output: io.IOBase) -> None:
    for location, printings in grouped.items():
        print(f"* {location}", file=output)
        for set_code, cards in printings.items():
            print(f"  * {set_code}", file=output)
            for card in cards:
                print(f"    * {card.name}, {card.collector_number}, {card.price_usd}", file=output)


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
    settings = read_settings(args.settings) if args.settings else {}

    # Merge hide: union of CLI set codes and settings list
    hidden: set[str] = set()
    if args.hide:
        hidden.update(code.strip() for code in args.hide.split(","))
    hidden.update(settings.get("hide", []))

    # collection and format: CLI overrides settings, then fall back to default
    collection = args.collection or settings.get("collection")
    fmt = args.format or (OutputFormat(settings["format"]) if "format" in settings else OutputFormat.TEXT)

    if args.file:
        with open(args.file) as f:
            names = read_card_names(f)
    else:
        names = read_card_names(sys.stdin)

    set_locations = read_collection(collection) if collection else None
    grouped = fetch_card_printings(names, set_locations)

    if hidden:
        grouped = {
            location: {k: v for k, v in sets.items() if k not in hidden}
            for location, sets in grouped.items()
        }
        grouped = {loc: sets for loc, sets in grouped.items() if sets}

    if args.output_file:
        output = open(args.output_file, "w")
    else:
        output = sys.stdout

    try:
        _FORMATTERS[fmt](grouped, output)
    finally:
        if args.output_file:
            output.close()
