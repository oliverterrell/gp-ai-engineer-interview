#!/usr/bin/env python3
"""
Product recommendation pipeline using LLM-only approach.

1. LLM classifies message intent + top 3 categories
2. Filter products by category + business rules
3. LLM selects top 3 products with reasoning

Usage:
    python recommend.py                          # Process all messages
    python recommend.py -o recommendations.csv   # Custom output path
"""

import argparse
import json
import time

import pandas as pd

from lib import llm, MIN_STOCK, MIN_RATING_DEFAULT, print_dataframe


CATEGORIES = [
    "Running Shoes",
    "Yoga",
    "Laptops",
    "Electronics",
    "Headphones",
    "Outerwear",
    "Water Bottles",
    "Kitchen",
    "Fitness",
    "Camping",
    "Wearables",
    "Audio",
    "Workwear",
    "Tablets",
    "Home",
]


def load_data(data_dir: str = "data") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load messages and products."""
    messages_df = pd.read_csv(f"{data_dir}/messages.csv")
    products_df = pd.read_csv(f"{data_dir}/products.csv")
    return messages_df, products_df


def filter_products(
    products_df: pd.DataFrame,
    categories: list[str],
    min_stock: int = MIN_STOCK,
    min_rating: float = MIN_RATING_DEFAULT,
) -> pd.DataFrame:
    """Filter products by category and business rules."""
    return products_df[
        (products_df["category"].isin(categories))
        & (products_df["stock_quantity"] >= min_stock)
        & (products_df["avg_rating"] >= min_rating)
        ]


def parse_json_response(text: str) -> dict | None:
    """Parse JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None


def classify_intent(message: str) -> dict:
    """
    First LLM call: Determine if user has purchase intent and get top 3 categories.

    Returns: {
        "should_recommend": bool,
        "categories": ["Category1", "Category2", "Category3"],
        "reasoning": "why this classification"
    }
    """
    prompt = f"""You are a product recommendation assistant. Analyze this user message:

"{message}"

Available product categories:
{json.dumps(CATEGORIES, indent=2)}

Determine:
1. Does this user have purchase intent? (looking to buy something vs just commenting/complaining)
2. If yes, which 3 categories are most relevant to their needs?

Return ONLY valid JSON (no markdown):
{{
    "should_recommend": true/false,
    "categories": ["Category1", "Category2", "Category3"],
    "reasoning": "brief explanation"
}}

If should_recommend is false, categories can be an empty array."""

    response = llm.generate_content(prompt)
    result = parse_json_response(response.text)

    if result is None:
        return {
            "should_recommend": False,
            "categories": [],
            "reasoning": "Failed to parse LLM response",
        }

    return result


def format_candidates_for_llm(candidates_df: pd.DataFrame) -> str:
    """Format candidate products for LLM prompt."""
    lines = []
    for _, p in candidates_df.iterrows():
        lines.append(
            f"- {p['product_id']}: {p['name']} | {p['category']} | ${p['price']:.2f} | {p['avg_rating']}★ | {p['description']}"
        )
    return "\n".join(lines)


def select_products(message: str, candidates_df: pd.DataFrame) -> dict:
    """
    Second LLM call: Select top 3 products from filtered candidates.

    Returns: {
        "recommendations": [
            {"product_id": "P0XX", "confidence": 0.0-1.0},
            ...
        ],
        "reasoning": "why these products in this order"
    }
    """
    if candidates_df.empty:
        return {
            "recommendations": [],
            "reasoning": "No products available in matching categories",
        }

    prompt = f"""You are a product recommendation assistant. A user sent this message:

"{message}"

Available products (in stock, good ratings):
{format_candidates_for_llm(candidates_df)}

Select the TOP 3 products that best match what the user is looking for, ranked by relevance.

Consider:
1. How well each product matches the user's stated need
2. Product quality (rating)
3. Value for the price point

Return ONLY valid JSON (no markdown):
{{
    "recommendations": [
        {{"product_id": "P0XX", "confidence": 0.95}},
        {{"product_id": "P0YY", "confidence": 0.80}},
        {{"product_id": "P0ZZ", "confidence": 0.65}}
    ],
    "reasoning": "One sentence explaining why these three products in this order"
}}

Confidence should reflect how well each product matches the user's needs (0.0-1.0)."""

    response = llm.generate_content(prompt)
    result = parse_json_response(response.text)

    if result is None:
        return {
            "recommendations": [],
            "reasoning": "Failed to parse LLM response",
        }

    return result


def recommend(message: str, products_df: pd.DataFrame) -> dict:
    """
    Full recommendation pipeline for a single message.

    Returns dict with classification and recommendations.
    """
    # Step 1: Classify intent and get categories
    classification = classify_intent(message)

    if not classification.get("should_recommend", False):
        return {
            "should_recommend": False,
            "categories": [],
            "recommendations": [],
            "reasoning": classification.get("reasoning", "No purchase intent detected"),
        }

    categories = classification.get("categories", [])

    # Step 2: Filter products
    candidates = filter_products(products_df, categories)

    # Step 3: LLM selection
    selection = select_products(message, candidates)

    return {
        "should_recommend": True,
        "categories": categories,
        "num_candidates": len(candidates),
        "recommendations": selection.get("recommendations", []),
        "reasoning": selection.get("reasoning", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate product recommendations")
    parser.add_argument("-o", "--output", default="recommendations.csv", help="Output CSV path")
    parser.add_argument("-d", "--data-dir", default="data", help="Data directory path")
    parser.add_argument("--message", type=str, required=False, help="Sample message to get a recommendation for.")
    args = parser.parse_args()

    # Load data
    print("Loading data...")
    messages_df, products_df = load_data(args.data_dir)

    if args.message:
        print("Finding personalized recommendations...")
        result = recommend(args.message, products_df)
        recs = result.get("recommendations", [])

        if not recs:
            print("\nNo recommendations - user does not appear to have purchase intent.")
            print(f"Reasoning: {result.get('reasoning', 'N/A')}")
        else:
            # Enrich recommendations with product details
            enriched_recs = []
            for rec in recs:
                product = products_df[products_df["product_id"] == rec["product_id"]].iloc[0]
                enriched_recs.append({
                    "product_id": rec["product_id"],
                    "name": product["name"],
                    "description": product["description"],
                    "price": f"${product['price']:.2f}",
                    "rating": f"{product['avg_rating']}★",
                    "confidence": rec["confidence"],
                })

            output_df = pd.DataFrame(enriched_recs)
            print(f"\nMESSAGE: {args.message}")
            print(f"\nCATEGORIES: {', '.join(result.get('categories', []))}")
            print("RECOMMENDATIONS:")
            print_dataframe(output_df)
            print(f"REASONING: {result.get('reasoning', 'N/A')}\n")
    else:
        # Process messages
        print(f"Processing {len(messages_df)} messages...")
        results = []

        for i, row in messages_df.iterrows():
            result = recommend(row["message"], products_df)

            # Extract top recommendation (or None if no recommendations)
            recs = result.get("recommendations", [])
            top_rec = recs[0] if recs else None

            results.append({
                "message_id": row["message_id"],
                "should_recommend": result["should_recommend"],
                "categories": ", ".join(result.get("categories", [])),
                "recommended_product_id": top_rec["product_id"] if top_rec else None,
                "confidence": top_rec["confidence"] if top_rec else None,
                "second_product_id": recs[1]["product_id"] if len(recs) > 1 else None,
                "second_confidence": recs[1]["confidence"] if len(recs) > 1 else None,
                "third_product_id": recs[2]["product_id"] if len(recs) > 2 else None,
                "third_confidence": recs[2]["confidence"] if len(recs) > 2 else None,
                "reasoning": result.get("reasoning", ""),
            })

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(messages_df)}")

            # Adhere to rate limit
            time.sleep(8)

        # Save output
        output_df = pd.DataFrame(results)
        output_df.to_csv(args.output, index=False)
        print(f"\nSaved recommendations to {args.output}")

        # Quick summary
        should_rec = output_df["should_recommend"].sum()
        has_rec = output_df["recommended_product_id"].notna().sum()
        print(f"Purchase intent detected: {should_rec}/{len(messages_df)}")
        print(f"Recommendations made: {has_rec}/{len(messages_df)}")


if __name__ == "__main__":
    main()
