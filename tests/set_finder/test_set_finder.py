import json
from argparse import Namespace
from io import StringIO
from unittest.mock import MagicMock, patch

from edh_utils.set_finder.set_finder import BASIC_LANDS, CardPrinting, DEFAULT_LOCATION, OutputFormat, _sort_grouped, set_finder


PRINTINGS = {
    DEFAULT_LOCATION: {
        "lea": [
            CardPrinting(name="Island", collector_number="288", price_usd="2.00"),
            CardPrinting(name="Swamp", collector_number="294", price_usd="1.00"),
        ],
    },
}

MULTI_SET_PRINTINGS = {
    DEFAULT_LOCATION: {
        "lea": [CardPrinting(name="Island", collector_number="288", price_usd="2.00")],
        "m21": [CardPrinting(name="Island", collector_number="267", price_usd="0.50")],
        "znr": [CardPrinting(name="Island", collector_number="271", price_usd="0.25")],
    },
}


def make_args(input_file=None, output_file=None, format=None, hide=None, collection=None, settings=None, price_level=None, include_basics=False, hide_uncollected=False):
    return Namespace(file=input_file, output_file=output_file, format=format, hide=hide, collection=collection, settings=settings, price_level=price_level, include_basics=include_basics, hide_uncollected=hide_uncollected)


@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_output_to_stdout(mock_fetch, mock_read, capsys):
    set_finder(make_args())
    captured = capsys.readouterr()
    assert "lea:" in captured.out
    assert "    Island #288 ($2.00)" in captured.out
    assert "    Swamp #294 ($1.00)" in captured.out


@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_output_to_file(mock_fetch, mock_read, tmp_path):
    out_file = tmp_path / "output.txt"
    set_finder(make_args(output_file=str(out_file)))
    content = out_file.read_text()
    assert "lea:" in content
    assert "    Island #288 ($2.00)" in content
    assert "    Swamp #294 ($1.00)" in content


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_text(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args())
    assert mock_stdout.getvalue() == (
        "Printings:\n"
        "  lea:\n"
        "    Island #288 ($2.00)\n"
        "    Swamp #294 ($1.00)\n"
    )


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_json(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.JSON))
    data = json.loads(mock_stdout.getvalue())
    assert list(data.keys()) == [DEFAULT_LOCATION]
    assert list(data[DEFAULT_LOCATION].keys()) == ["lea"]
    assert data[DEFAULT_LOCATION]["lea"][0] == {"name": "Island", "collector_number": "288", "price_usd": "2.00"}
    assert data[DEFAULT_LOCATION]["lea"][1] == {"name": "Swamp", "collector_number": "294", "price_usd": "1.00"}


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_csv(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.CSV))
    lines = mock_stdout.getvalue().splitlines()
    assert lines[0] == "set,collector_number,name,price_usd,location"
    assert lines[1] == "lea,288,Island,2.00,unknown"
    assert lines[2] == "lea,294,Swamp,1.00,unknown"


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_md(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.MD))
    assert mock_stdout.getvalue() == (
        "* Printings\n"
        "  * lea\n"
        "    * Island, 288, 2.00\n"
        "    * Swamp, 294, 1.00\n"
    )


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
def test_hide_single_set(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide="lea"))
    output = mock_stdout.getvalue()
    assert "lea" not in output
    assert "m21" in output
    assert "znr" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
def test_hide_multiple_sets(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide="lea,m21"))
    output = mock_stdout.getvalue()
    assert "lea" not in output
    assert "m21" not in output
    assert "znr" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
def test_hide_none_shows_all_sets(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide=None))
    output = mock_stdout.getvalue()
    assert "lea" in output
    assert "m21" in output
    assert "znr" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value={
    "binder": {"lea": [CardPrinting(name="Island", collector_number="288", price_usd="2.00")]},
    DEFAULT_LOCATION: {"m21": [CardPrinting(name="Island", collector_number="267", price_usd="0.50")]},
})
def test_format_csv_with_collection(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.CSV))
    lines = mock_stdout.getvalue().splitlines()
    assert lines[0] == "set,collector_number,name,price_usd,location"
    assert "lea,288,Island,2.00,binder" in lines
    assert "m21,267,Island,0.50,unknown" in lines


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"hide": ["lea"]})
def test_settings_hide_merges_with_cli_hide(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide="m21", settings="settings.toml"))
    output = mock_stdout.getvalue()
    assert "lea" not in output
    assert "m21" not in output
    assert "znr" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"format": "md"})
def test_settings_format_used_when_cli_not_provided(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(settings="settings.toml"))
    output = mock_stdout.getvalue()
    assert output.startswith("* ")


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"format": "md"})
def test_cli_format_overrides_settings(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.JSON, settings="settings.toml"))
    data = json.loads(mock_stdout.getvalue())
    assert isinstance(data, dict)


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.read_collection", return_value=None)
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"collection": "col.json"})
def test_settings_collection_used_when_cli_not_provided(mock_settings, mock_fetch, mock_collection, mock_read, mock_stdout):
    set_finder(make_args(settings="settings.toml"))
    mock_collection.assert_called_once_with("col.json")


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.read_collection", return_value=None)
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=MULTI_SET_PRINTINGS)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"collection": "col.json"})
def test_cli_collection_overrides_settings(mock_settings, mock_fetch, mock_collection, mock_read, mock_stdout):
    set_finder(make_args(collection="cli.json", settings="settings.toml"))
    mock_collection.assert_called_once_with("cli.json")


# --- _sort_grouped ---

UNSORTED_GROUPED = {
    DEFAULT_LOCATION: {"lea": []},
    "zebra": {"m21": []},
    "alpha": {"znr": []},
    "binder": {"eld": []},
}


def test_sort_grouped_alphanumeric_default_last():
    result = _sort_grouped(UNSORTED_GROUPED)
    assert list(result.keys()) == ["alpha", "binder", "zebra", DEFAULT_LOCATION]


def test_sort_grouped_without_default_location():
    grouped = {"zebra": {}, "alpha": {}, "binder": {}}
    assert list(_sort_grouped(grouped).keys()) == ["alpha", "binder", "zebra"]


def test_sort_grouped_only_default_location():
    grouped = {DEFAULT_LOCATION: {}}
    assert list(_sort_grouped(grouped).keys()) == [DEFAULT_LOCATION]


def test_sort_grouped_empty():
    assert _sort_grouped({}) == {}


# --- --include-basics ---

@patch("edh_utils.set_finder.set_finder.fetch_card_printings")
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp", "Opt"])
def test_basics_excluded_by_default(mock_read, mock_fetch):
    mock_fetch.return_value = {}
    set_finder(make_args())
    names_passed = mock_fetch.call_args[0][0]
    assert "Swamp" not in names_passed
    assert "Opt" in names_passed


@patch("edh_utils.set_finder.set_finder.fetch_card_printings")
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp", "Opt"])
def test_basics_included_with_flag(mock_read, mock_fetch):
    mock_fetch.return_value = {}
    set_finder(make_args(include_basics=True))
    names_passed = mock_fetch.call_args[0][0]
    assert "Swamp" in names_passed
    assert "Opt" in names_passed


@patch("edh_utils.set_finder.set_finder.fetch_card_printings")
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["SWAMP", "Forest", "plains"])
def test_basics_excluded_case_insensitive(mock_read, mock_fetch):
    mock_fetch.return_value = {}
    set_finder(make_args())
    names_passed = mock_fetch.call_args[0][0]
    assert names_passed == []


def test_basic_lands_constant_contains_five_classics():
    assert BASIC_LANDS == {"plains", "island", "swamp", "mountain", "forest"}


@patch("edh_utils.set_finder.set_finder.fetch_card_printings")
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp", "Opt"])
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"include_basics": True})
def test_settings_include_basics_used_when_cli_not_set(mock_settings, mock_read, mock_fetch):
    mock_fetch.return_value = {}
    set_finder(make_args(settings="settings.toml"))
    names_passed = mock_fetch.call_args[0][0]
    assert "Swamp" in names_passed
    assert "Opt" in names_passed


@patch("edh_utils.set_finder.set_finder.fetch_card_printings")
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Swamp", "Opt"])
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"include_basics": False})
def test_cli_include_basics_overrides_settings(mock_settings, mock_read, mock_fetch):
    mock_fetch.return_value = {}
    set_finder(make_args(include_basics=True, settings="settings.toml"))
    names_passed = mock_fetch.call_args[0][0]
    assert "Swamp" in names_passed


# --- --hide-uncollected ---

COLLECTED_AND_UNCOLLECTED = {
    "binder": {"lea": [CardPrinting(name="Island", collector_number="288", price_usd="2.00")]},
    DEFAULT_LOCATION: {"m21": [CardPrinting(name="Island", collector_number="267", price_usd="0.50")]},
}


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=COLLECTED_AND_UNCOLLECTED)
def test_hide_uncollected_removes_default_location(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide_uncollected=True))
    output = mock_stdout.getvalue()
    assert DEFAULT_LOCATION not in output
    assert "binder" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=COLLECTED_AND_UNCOLLECTED)
def test_hide_uncollected_false_shows_default_location(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide_uncollected=False))
    output = mock_stdout.getvalue()
    assert DEFAULT_LOCATION in output
    assert "binder" in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=COLLECTED_AND_UNCOLLECTED)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"hide_uncollected": True})
def test_settings_hide_uncollected_used_when_cli_not_set(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(settings="settings.toml"))
    output = mock_stdout.getvalue()
    assert DEFAULT_LOCATION not in output


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=COLLECTED_AND_UNCOLLECTED)
@patch("edh_utils.set_finder.set_finder.read_settings", return_value={"hide_uncollected": False})
def test_cli_hide_uncollected_overrides_settings(mock_settings, mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(hide_uncollected=True, settings="settings.toml"))
    output = mock_stdout.getvalue()
    assert DEFAULT_LOCATION not in output
