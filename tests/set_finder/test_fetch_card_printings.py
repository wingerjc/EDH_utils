from unittest.mock import patch

from edh_utils.set_finder.set_finder import CardPrinting, DEFAULT_LOCATION, fetch_card_printings


def make_card(name: str, set_code: str, collector_number: str, price_usd: str | None = "1.00") -> dict:
    return {
        "name": name,
        "set": set_code,
        "collector_number": collector_number,
        "prices": {"usd": price_usd},
    }


@patch("edh_utils.set_finder.set_finder.search")
def test_single_card_single_set(mock_search):
    card = make_card("Swamp", "lea", "294")
    mock_search.return_value = [card]
    result = fetch_card_printings(["Swamp"])
    assert result == {
        DEFAULT_LOCATION: {"lea": [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]}
    }


@patch("edh_utils.set_finder.set_finder.search")
def test_single_card_multiple_sets(mock_search):
    mock_search.return_value = [
        make_card("Swamp", "lea", "294"),
        make_card("Swamp", "m21", "312"),
    ]
    result = fetch_card_printings(["Swamp"])
    assert result[DEFAULT_LOCATION]["lea"] == [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]
    assert result[DEFAULT_LOCATION]["m21"] == [CardPrinting(name="Swamp", collector_number="312", price_usd="1.00")]


@patch("edh_utils.set_finder.set_finder.search")
def test_multiple_cards_same_set(mock_search):
    def side_effect(query):
        if "Swamp" in query:
            return [make_card("Swamp", "lea", "294")]
        if "Island" in query:
            return [make_card("Island", "lea", "288")]
        return []

    mock_search.side_effect = side_effect
    result = fetch_card_printings(["Swamp", "Island"])

    assert len(result[DEFAULT_LOCATION]["lea"]) == 2
    assert CardPrinting(name="Swamp", collector_number="294", price_usd="1.00") in result[DEFAULT_LOCATION]["lea"]
    assert CardPrinting(name="Island", collector_number="288", price_usd="1.00") in result[DEFAULT_LOCATION]["lea"]


@patch("edh_utils.set_finder.set_finder.search")
def test_cards_sorted_by_name_within_set(mock_search):
    mock_search.return_value = [
        make_card("Swamp", "lea", "294"),
        make_card("Island", "lea", "288"),
        make_card("Forest", "lea", "295"),
    ]
    result = fetch_card_printings(["Swamp"])
    assert [c.name for c in result[DEFAULT_LOCATION]["lea"]] == ["Forest", "Island", "Swamp"]


@patch("edh_utils.set_finder.set_finder.search")
def test_empty_card_list(mock_search):
    result = fetch_card_printings([])
    mock_search.assert_not_called()
    assert result == {}


@patch("edh_utils.set_finder.set_finder.search")
def test_price_usd_none(mock_search):
    mock_search.return_value = [make_card("Swamp", "lea", "294", price_usd=None)]
    result = fetch_card_printings(["Swamp"])
    assert result[DEFAULT_LOCATION]["lea"][0].price_usd is None


@patch("edh_utils.set_finder.set_finder.search")
def test_with_collection_assigns_location(mock_search):
    mock_search.return_value = [make_card("Swamp", "lea", "294")]
    result = fetch_card_printings(["Swamp"], set_locations={"lea": ["binder"]})
    assert "binder" in result
    assert DEFAULT_LOCATION not in result
    assert result["binder"]["lea"] == [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]


@patch("edh_utils.set_finder.set_finder.search")
def test_with_collection_set_not_found_uses_default(mock_search):
    mock_search.return_value = [make_card("Swamp", "lea", "294")]
    result = fetch_card_printings(["Swamp"], set_locations={"m21": ["binder"]})
    assert DEFAULT_LOCATION in result
    assert result[DEFAULT_LOCATION]["lea"] == [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]


@patch("edh_utils.set_finder.set_finder.search")
def test_with_collection_set_in_multiple_locations(mock_search):
    mock_search.return_value = [make_card("Swamp", "lea", "294")]
    result = fetch_card_printings(["Swamp"], set_locations={"lea": ["binder", "box"]})
    assert "binder" in result
    assert "box" in result
    assert result["binder"]["lea"] == [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]
    assert result["box"]["lea"] == [CardPrinting(name="Swamp", collector_number="294", price_usd="1.00")]
