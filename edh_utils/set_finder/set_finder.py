import csv
import enum
import io
import json
import sys
import tomllib

from pydantic import BaseModel

from edh_utils.logging import logger
from edh_utils.scryfall import search

log = logger()

DEFAULT_LOCATION = "Printings"
BASIC_LANDS = frozenset({"plains", "island", "swamp", "mountain", "forest"})


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

    Supported keys: hide (list of set codes), collection (file path),
    format (output format), price_level (list of price thresholds).
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


def parse_price_levels(raw: str) -> list[float]:
    """Parse a comma-separated string of price thresholds into a sorted list of floats."""
    return sorted(float(p.strip()) for p in raw.split(","))


def price_signs(price_usd: str | None, levels: list[float]) -> str:
    """Return a string of '$' characters based on how many price thresholds the card meets.

    The count equals the number of thresholds the price is greater than or equal to.
    Returns an empty string if price_usd is None or no thresholds are met.
    """
    if price_usd is None or not levels:
        return ""
    price = float(price_usd)
    return "".join(["$" for level in levels if price >= level])


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
        result = search(f'!"{name}" unique:prints')
        if result.error:
            log.error(f"Card not found on Scryfall: {result.error.query!r}")
            continue
        for card in result.payload:
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


def _sort_grouped(
    grouped: dict[str, dict[str, list[CardPrinting]]],
) -> dict[str, dict[str, list[CardPrinting]]]:
    """Return grouped with locations sorted alphanumerically, DEFAULT_LOCATION last."""
    keys = sorted(k for k in grouped if k != DEFAULT_LOCATION)
    if DEFAULT_LOCATION in grouped:
        keys.append(DEFAULT_LOCATION)
    return {k: grouped[k] for k in keys}


def _format_text(
    grouped: dict[str, dict[str, list[CardPrinting]]],
    output: io.IOBase,
    price_levels: list[float],
) -> None:
    for location, printings in _sort_grouped(grouped).items():
        print(f"{location}:", file=output)
        for set_code, cards in printings.items():
            print(f"  {set_code}:", file=output)
            for card in cards:
                signs = price_signs(card.price_usd, price_levels)
                suffix = f" {signs}" if signs else ""
                print(f"    {card.name} #{card.collector_number} (${card.price_usd}){suffix}", file=output)


def _format_json(
    grouped: dict[str, dict[str, list[CardPrinting]]],
    output: io.IOBase,
    price_levels: list[float],
) -> None:
    data = {
        location: {
            set_code: [card.model_dump() for card in cards]
            for set_code, cards in printings.items()
        }
        for location, printings in grouped.items()
    }
    print(json.dumps(data, indent=2), file=output)


def _format_csv(
    grouped: dict[str, dict[str, list[CardPrinting]]],
    output: io.IOBase,
    price_levels: list[float],
) -> None:
    writer = csv.writer(output)
    writer.writerow(["set", "collector_number", "name", "price_usd", "location"])
    for location, printings in grouped.items():
        loc_display = "unknown" if location == DEFAULT_LOCATION else location
        for set_code, cards in printings.items():
            for card in cards:
                writer.writerow([set_code, card.collector_number, card.name, card.price_usd, loc_display])


def _format_md(
    grouped: dict[str, dict[str, list[CardPrinting]]],
    output: io.IOBase,
    price_levels: list[float],
) -> None:
    for location, printings in _sort_grouped(grouped).items():
        print(f"* {location}", file=output)
        for set_code, cards in printings.items():
            print(f"  * {set_code}", file=output)
            for card in cards:
                signs = price_signs(card.price_usd, price_levels)
                card_info = f"{card.name}, {card.collector_number}, {card.price_usd}{' ' + signs if signs else ''}"
                if signs:
                    card_info = f"**{card_info}**"
                print(f"    * {card_info}", file=output)


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

    # collection, format, price_level: CLI overrides settings, then fall back to defaults
    collection = args.collection or settings.get("collection")
    fmt = args.format or (OutputFormat(settings["format"]) if "format" in settings else OutputFormat.TEXT)
    if args.price_level:
        price_levels = parse_price_levels(args.price_level)
    elif "price_level" in settings:
        price_levels = sorted(float(p) for p in settings["price_level"])
    else:
        price_levels = []

    if args.file:
        with open(args.file) as f:
            names = read_card_names(f)
    else:
        names = read_card_names(sys.stdin)

    include_basics = args.include_basics or settings.get("include_basics", False)
    if not include_basics:
        filtered = [n for n in names if n.lower() in BASIC_LANDS]
        for name in filtered:
            log.info(f"Skipping basic land: {name!r}")
        names = [n for n in names if n.lower() not in BASIC_LANDS]

    set_locations = read_collection(collection) if collection else None
    grouped = fetch_card_printings(names, set_locations)

    if hidden:
        grouped = {
            location: {k: v for k, v in sets.items() if k not in hidden}
            for location, sets in grouped.items()
        }
        grouped = {loc: sets for loc, sets in grouped.items() if sets}

    hide_uncollected = args.hide_uncollected or settings.get("hide_uncollected", False)
    if hide_uncollected:
        grouped = {k: v for k, v in grouped.items() if k != DEFAULT_LOCATION}

    if args.output_file:
        output = open(args.output_file, "w")
    else:
        output = sys.stdout

    try:
        _FORMATTERS[fmt](grouped, output, price_levels)
    finally:
        if args.output_file:
            output.close()
