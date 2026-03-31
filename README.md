# EDH_utils
MTG utilities for sorting, searching, and finding cards.

The projects are:
* set-finder: finds possible sets for a list of cards.

## Usage

```
usage: edh-utils [-h] {set-finder} ...

positional arguments:
  {set-finder}

options:
  -h, --help    show this help message and exit

usage: edh-utils set-finder [-h] [-f FILE] [-o FILE] [-s FILE] [-p PRICES]
                            [-c FILE] [--hide SETS]
                            [--format {text,json,csv,md}]

options:
  -h, --help            show this help message and exit
  -f, --file FILE       Input file (default: stdin)
  -o, --output-file FILE
                        Output file (default: stdout)
  -s, --settings FILE   TOML settings file
  -p, --price-level PRICES
                        Comma-separated price thresholds for dollar-sign
                        indicators
  -c, --collection FILE
                        JSON file mapping locations to set codes
  --hide SETS           Comma-separated list of set codes to exclude from
                        output
  --format {text,json,csv,md}
                        Output format (default: text)
```

## set-finder

### Settings file

The `--settings` / `-s` option accepts a TOML file that sets default values for
`hide`, `collection`, and `format`. CLI options `--collection` and `--format`
override the settings file; `--hide` is additive (CLI and settings sets are
merged).

Example `settings.toml`:

```toml
# All settings are optional.
hide = ["lea", "usg"]
collection = "path/to/my_collection.json"
format = "text"
price_level = [2.0, 5.0]
```
