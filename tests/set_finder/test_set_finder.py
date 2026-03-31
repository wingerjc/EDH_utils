from argparse import Namespace
from io import StringIO
from unittest.mock import patch

from edh_utils.set_finder.set_finder import CardPrinting, set_finder


PRINTINGS = {
    "lea": [
        CardPrinting(name="Island", collector_number="288", price_usd="2.00"),
        CardPrinting(name="Swamp", collector_number="294", price_usd="1.00"),
    ],
}


def make_args(input_file=None, output_file=None):
    return Namespace(file=input_file, output_file=output_file)


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
def test_output_format(mock_fetch, mock_read, mock_stdout):
    set_finder(make_args())
    assert mock_stdout.getvalue() == "lea:\n  Island #288 ($2.00)\n  Swamp #294 ($1.00)\n"
