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

usage: edh-utils set-finder [-h] [-f FILE] [-o FILE]
                            [--format {text,json,csv,md}]

options:
  -h, --help            show this help message and exit
  -f, --file FILE       Input file (default: stdin)
  -o, --output-file FILE
                        Output file (default: stdout)
  --format {text,json,csv,md}
                        Output format (default: text)
```
