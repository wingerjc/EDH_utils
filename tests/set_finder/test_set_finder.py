import json
from argparse import Namespace
from io import StringIO
from unittest.mock import patch

from edh_utils.set_finder.set_finder import CardPrinting, OutputFormat, set_finder


PRINTINGS = {
    "lea": [
        CardPrinting(name="Island", collector_number="288", price_usd="2.00"),
        CardPrinting(name="Swamp", collector_number="294", price_usd="1.00"),
    ],
}


def make_args(input_file=None, output_file=None, format=OutputFormat.TEXT):
    return Namespace(file=input_file, output_file=output_file, format=format)


@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_output_to_stdout(mock_fetch, mock_read, capsys):
    set_finder(make_args())
    captured = capsys.readouterr()
    assert "lea:" in captured.out
    assert "  Island #288 ($2.00)" in captured.out
    assert "  Swamp #294 ($1.00)" in captured.out


@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_output_to_file(mock_fetch, mock_read, tmp_path):
    out_file = tmp_path / "output.txt"
    set_finder(make_args(output_file=str(out_file)))
    content = out_file.read_text()
    assert "lea:" in content
    assert "  Island #288 ($2.00)" in content
    assert "  Swamp #294 ($1.00)" in content


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_text(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.TEXT))
    assert mock_stdout.getvalue() == "lea:\n  Island #288 ($2.00)\n  Swamp #294 ($1.00)\n"


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_json(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.JSON))
    data = json.loads(mock_stdout.getvalue())
    assert list(data.keys()) == ["lea"]
    assert len(data["lea"]) == 2
    assert data["lea"][0] == {"name": "Island", "collector_number": "288", "price_usd": "2.00"}
    assert data["lea"][1] == {"name": "Swamp", "collector_number": "294", "price_usd": "1.00"}


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_csv(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.CSV))
    lines = mock_stdout.getvalue().splitlines()
    assert lines[0] == "set,collector_number,name,price_usd"
    assert lines[1] == "lea,288,Island,2.00"
    assert lines[2] == "lea,294,Swamp,1.00"


@patch("sys.stdout", new_callable=StringIO)
@patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"])
@patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS)
def test_format_md(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args(format=OutputFormat.MD))
    assert mock_stdout.getvalue() == (
        "* lea\n"
        "  * Island, 288, 2.00\n"
        "  * Swamp, 294, 1.00\n"
    )
