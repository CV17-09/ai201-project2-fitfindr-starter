"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.
"""

import re

from tools import search_listings, suggest_outfit, create_fit_card


def _new_session(query: str, wardrobe: dict) -> dict:
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


def _parse_query(query: str) -> dict:
    """
    Simple rule-based parser for description, size, and max_price.
    """
    query_lower = query.lower()

    price_match = re.search(r"(?:under|below|less than|\$)\s*\$?(\d+(?:\.\d+)?)", query_lower)
    max_price = float(price_match.group(1)) if price_match else None

    size_match = re.search(r"\bsize\s+([a-z0-9/]+)\b", query_lower)
    size = size_match.group(1).upper() if size_match else None

    description = query_lower

    description = re.sub(r"(?:under|below|less than)\s*\$?\d+(?:\.\d+)?", "", description)
    description = re.sub(r"\$\d+(?:\.\d+)?", "", description)
    description = re.sub(r"\bsize\s+[a-z0-9/]+\b", "", description)
    description = description.replace("looking for", "")
    description = description.replace("i'm", "")
    description = description.replace("im", "")
    description = description.replace("i am", "")
    description = description.strip(" ,.")

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


def run_agent(query: str, wardrobe: dict) -> dict:
    session = _new_session(query, wardrobe)

    parsed = _parse_query(query)
    session["parsed"] = parsed

    results = search_listings(
        description=parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )
    session["search_results"] = results

    if not results:
        session["error"] = (
            "No listings matched your search. Try using a broader description, "
            "removing the size filter, or increasing your max price."
        )
        return session

    session["selected_item"] = results[0]

    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=session["wardrobe"],
    )

    if not session["outfit_suggestion"]:
        session["error"] = "I found an item, but I could not create an outfit suggestion."
        return session

    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"],
    )

    if not session["fit_card"]:
        session["error"] = "I created an outfit, but I could not create a fit card."
        return session

    return session


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )

    print("Parsed:", session["parsed"])
    print("Selected item:", session["selected_item"])
    print("Outfit suggestion:", session["outfit_suggestion"])
    print("Fit card:", session["fit_card"])
    print("Error:", session["error"])

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )

    print("Parsed:", session2["parsed"])
    print("Selected item:", session2["selected_item"])
    print("Outfit suggestion:", session2["outfit_suggestion"])
    print("Fit card:", session2["fit_card"])
    print("Error:", session2["error"])