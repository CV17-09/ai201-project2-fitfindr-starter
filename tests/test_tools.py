from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_empty_wardrobe


def test_search_returns_results():
    results = search_listings(
        "vintage graphic tee",
        size=None,
        max_price=50
    )

    assert isinstance(results, list)


def test_search_empty_results():
    results = search_listings(
        "designer ballgown",
        size="XXS",
        max_price=5
    )

    assert results == []


def test_search_price_filter():
    results = search_listings(
        "jacket",
        size=None,
        max_price=10
    )

    assert all(item["price"] <= 10 for item in results)


def test_suggest_outfit_empty_wardrobe():
    item = {
        "title": "Faded Band Tee",
        "price": 22,
        "platform": "Depop"
    }

    result = suggest_outfit(
        item,
        get_empty_wardrobe()
    )

    assert isinstance(result, str)
    assert len(result) > 0


def test_create_fit_card_missing_outfit():
    item = {
        "title": "Faded Band Tee",
        "price": 22,
        "platform": "Depop"
    }

    result = create_fit_card("", item)

    assert isinstance(result, str)
    assert "outfit" in result.lower()