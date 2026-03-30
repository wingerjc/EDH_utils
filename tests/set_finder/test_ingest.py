import io

from edh_utils.set_finder.set_finder import read_card_names


def card_input(lines: list[str]) -> io.StringIO:
    return io.StringIO("\n".join(lines))


def test_name_only():
    result = read_card_names(card_input(["Swamp"]))
    assert result == ["Swamp"]


def test_name_with_count():
    result = read_card_names(card_input(["4 Swamp"]))
    assert result == ["Swamp"]


def test_multiple_with_counts():
    result = read_card_names(card_input(["4 Swamp", "2 Island", "3 Forest"]))
    assert result == ["Forest", "Island", "Swamp"]


def test_mixed_count_and_no_count():
    result = read_card_names(card_input(["4 Swamp", "Island"]))
    assert result == ["Island", "Swamp"]


def test_dedup_same_name():
    result = read_card_names(card_input(["Swamp", "Swamp"]))
    assert result == ["Swamp"]


def test_dedup_count_and_no_count():
    result = read_card_names(card_input(["2 Swamp", "Swamp"]))
    assert result == ["Swamp"]


def test_empty_input():
    result = read_card_names(card_input([]))
    assert result == []
