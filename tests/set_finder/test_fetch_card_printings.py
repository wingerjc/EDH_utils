from unittest.mock import patch

from edh_utils.set_finder.set_finder import CardPrinting, fetch_card_printings


def make_card(name: str, set_code: str, collector_number: str, price_usd: str | None = "1.00") -> dict:
    return {
        "name": name,
        "set": set_code,
        "collector_number": collector_number,
        "prices": {"usd": price_usd},
    }


def test_single_card_single_set():
    card = make_card("Swamp", "lea", "294")
    with patch("edh_utils.set_finder.set_finder.search", return_value=[card]):
        result = fetch_card_printings(["Swamp"])
    assert result == {"lea": [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]}


def test_single_card_multiple_sets():
    cards = [
        make_card("Swamp", "lea", "294"),
        make_card("Swamp", "m21", "312"),
    ]
    with patch("edh_utils.set_finder.set_finder.search", return_value=cards):
        result = fetch_card_printings(["Swamp"])
    assert "lea" in result
    assert "m21" in result
    assert result["lea"] == [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]
    assert result["m21"] == [CardPrinting(name="Swamp", collector_number="312", price_usd="1.00")]


def test_multiple_cards_same_set():
    def mock_search(query):
        if "Swamp" in query:
            return [make_card("Swamp", "lea", "294")]
        if "Island" in query:
            return [make_card("Island", "lea", "288")]
        return []

    with patch("edh_utils.set_finder.set_finder.search", side_effect=mock_search):
        result = fetch_card_printings(["Swamp", "Island"])

    assert len(result["lea"]) == 2
    assert CardPrinting(name="Swamp", collector_number="294", price_usd="1.00") in result["lea"]
    assert CardPrinting(name="Island", collector_number="288", price_usd="1.00") in result["lea"]


def test_cards_sorted_by_name_within_set():
    cards = [
        make_card("Swamp", "lea", "294"),
        make_card("Island", "lea", "288"),
        make_card("Forest", "lea", "295"),
    ]
    with patch("edh_utils.set_finder.set_finder.search", return_value=cards):
        result = fetch_card_printings(["Swamp"])
    assert [c.name for c in result["lea"]] == ["Forest", "Island", "Swamp"]


def test_empty_card_list():
    with patch("edh_utils.set_finder.set_finder.search") as mock_search:
        result = fetch_card_printings([])
    mock_search.assert_not_called()
    assert result == {}


def test_price_usd_none():
    card = make_card("Swamp", "lea", "294", price_usd=None)
    with patch("edh_utils.set_finder.set_finder.search", return_value=[card]):
        result = fetch_card_printings(["Swamp"])
    assert result["lea"][0].price_usd is None
