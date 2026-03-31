from unittest.mock import patch
from io import StringIO

from edh_utils.set_finder.set_finder import (
    CardPrinting,
    DEFAULT_LOCATION,
    OutputFormat,
    parse_price_levels,
    price_signs,
    set_finder,
)
from argparse import Namespace


PRINTINGS = {
    DEFAULT_LOCATION: {
        "lea": [
            CardPrinting(name="Swamp", collector_number="294", price_usd="0.50"),
            CardPrinting(name="Island", collector_number="288", price_usd="3.00"),
            CardPrinting(name="Forest", collector_number="295", price_usd="5.00"),
            CardPrinting(name="Mountain", collector_number="289", price_usd=None),
        ],
    },
}


def make_args(**kwargs):
    defaults = dict(
        file=None, output_file=None, format=None, hide=None,
        collection=None, settings=None, price_level=None, include_basics=False, hide_uncollected=False,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


# --- parse_price_levels ---

def test_parse_single():
    assert parse_price_levels("2") == [2.0]


def test_parse_multiple_unsorted():
    assert parse_price_levels("5,2") == [2.0, 5.0]


def test_parse_with_spaces():
    assert parse_price_levels("2, 5") == [2.0, 5.0]


# --- price_signs ---

def test_below_all_thresholds():
    assert price_signs("0.50", [2.0, 5.0]) == ""


def test_meets_one_threshold():
    assert price_signs("3.00", [2.0, 5.0]) == "$"


def test_meets_all_thresholds():
    assert price_signs("5.00", [2.0, 5.0]) == "$$"


def test_price_none_returns_empty():
    assert price_signs(None, [2.0, 5.0]) == ""


def test_no_levels_returns_empty():
    assert price_signs("10.00", []) == ""


def test_exact_threshold():
    assert price_signs("2.00", [2.0, 5.0]) == "$"


# --- format integration ---

@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_text_appends_signs(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(price_level="2,5"))
    output = mock_stdout.getvalue()
    assert "Swamp #294 ($0.50)\n" in output       # below threshold, no signs
    assert "Island #288 ($3.00) $\n" in output    # one sign
    assert "Forest #295 ($5.00) $$\n" in output   # two signs
    assert "Mountain #289 ($None)\n" in output    # None price, no signs


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_md_bolds_and_appends_signs(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.MD, price_level="2,5"))
    output = mock_stdout.getvalue()
    assert "    * Swamp, 294, 0.50\n" in output                          # no bold, no signs
    assert "    * **Island, 288, 3.00 $**\n" in output                  # bold + one sign
    assert "    * **Forest, 295, 5.00 $$**\n" in output                 # bold + two signs
    assert "    * Mountain, 289, None\n" in output                      # None price, no bold


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"price_level": [2.0, 5.0]})
def test_settings_price_level_used(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(settings="settings.toml"))
    output = mock_stdout.getvalue()
    assert "Island #288 ($3.00) $\n" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"price_level": [10.0]})
def test_cli_price_level_overrides_settings(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(price_level="2,5", settings="settings.toml"))
    output = mock_stdout.getvalue()
    assert "Island #288 ($3.00) $\n" in output    # CLI [2,5] used, not settings [10]
