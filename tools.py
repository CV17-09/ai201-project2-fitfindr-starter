"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.
    """
    listings = load_listings()

    query_words = set(description.lower().split())
    results = []

    for item in listings:
        if max_price is not None and item.get("price", 0) > max_price:
            continue

        if size:
            item_size = str(item.get("size", "")).lower()
            if size.lower() not in item_size:
                continue

        searchable_text = " ".join([
            str(item.get("title", "")),
            str(item.get("description", "")),
            str(item.get("category", "")),
            " ".join(item.get("style_tags", [])),
            " ".join(item.get("colors", [])),
            str(item.get("brand", "")),
            str(item.get("platform", "")),
        ]).lower()

        score = sum(1 for word in query_words if word in searchable_text)

        if score > 0:
            results.append((score, item))

    results.sort(key=lambda pair: pair[0], reverse=True)
    return [item for score, item in results]


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.
    """
    if not new_item:
        return "I need a thrifted item before I can suggest an outfit."

    wardrobe_items = wardrobe.get("items", []) if wardrobe else []

    client = _get_groq_client()

    if not wardrobe_items:
        prompt = f"""
You are FitFindr, a helpful secondhand fashion styling assistant.

The user is considering this thrifted item:
{new_item}

The user's wardrobe is empty or unavailable.

Suggest 1-2 complete outfit ideas using common wardrobe basics.
Mention the overall vibe and keep it practical.
Return 3-5 sentences.
"""
    else:
        prompt = f"""
You are FitFindr, a helpful secondhand fashion styling assistant.

The user is considering this thrifted item:
{new_item}

The user's wardrobe items:
{wardrobe_items}

Suggest 1-2 complete outfits using the thrifted item and specific pieces from the wardrobe.
Mention the overall vibe and keep it practical.
Return 3-5 sentences.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    return response.choices[0].message.content.strip()


def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    """
    if not outfit or not outfit.strip():
        return "I need an outfit suggestion before I can create a fit card."

    if not new_item:
        return "I need a thrifted item before I can create a fit card."

    client = _get_groq_client()

    title = new_item.get("title", "thrifted find")
    price = new_item.get("price", "unknown price")
    platform = new_item.get("platform", "a secondhand platform")

    prompt = f"""
You are FitFindr, a casual fashion caption writer.

Create a 2-4 sentence outfit caption for Instagram or TikTok.

Item name: {title}
Price: {price}
Platform: {platform}
Outfit suggestion: {outfit}

Requirements:
- Mention the item name, price, and platform naturally once.
- Make it sound casual and authentic, not like a product description.
- Capture the outfit vibe with specific details.
- Keep it short and shareable.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
    )

    return response.choices[0].message.content.strip()