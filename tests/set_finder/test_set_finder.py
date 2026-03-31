import sys
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


def test_output_to_stdout(capsys):
    with patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS):
        with patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"]):
            set_finder(make_args())

    captured = capsys.readouterr()
    assert "lea:" in captured.out
    assert "  Island #288 ($2.00)" in captured.out
    assert "  Swamp #294 ($1.00)" in captured.out


def test_output_to_file(tmp_path):
    out_file = tmp_path / "output.txt"
    with patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS):
        with patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"]):
            set_finder(make_args(output_file=str(out_file)))

    content = out_file.read_text()
    assert "lea:" in content
    assert "  Island #288 ($2.00)" in content
    assert "  Swamp #294 ($1.00)" in content


def test_output_format():
    with patch("edh_utils.set_finder.set_finder.fetch_card_printings", return_value=PRINTINGS):
        with patch("edh_utils.set_finder.set_finder.read_card_names", return_value=["Island", "Swamp"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                set_finder(make_args())
                output = mock_stdout.getvalue()

    assert output == "lea:\n  Island #288 ($2.00)\n  Swamp #294 ($1.00)\n"
