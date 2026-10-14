#!/usr/bin/env python3
"""Create examples using the actual EU allergen wording found on Coop labels."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

SOURCE_PATH = Path(__file__).resolve().parents[1] / "data" / "coop_products_detailed_sample.json"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "allergen_examples.json"
CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "allergen_examples.csv"

SAFE_PATTERNS = [
    "non contiene glutine",
    "senza glutine",
    "non contiene",
    "senza noci",
    "senza arachidi",
    "senza nocciola",
    "vegano e senza glutine",
]

EU_NUT_PATTERNS = [
    "può contenere arachidi",
    "puo contenere arachidi",
    "potrebbe contenere arachidi",
    "può contenere anacardi",
    "puo contenere anacardi",
    "può contenere mandorle",
    "puo contenere mandorle",
    "può contenere nocciole",
    "puo contenere nocciole",
    "può contenere noci",
    "puo contenere noci",
    "può contenere pistacchi",
    "puo contenere pistacchi",
    "può contenere tracce di altri cereali contenenti glutine",
    "puo contenere tracce di altri cereali contenenti glutine",
    "potrebbe contenere cereali contenenti glutine",
    "può contenere soia",
    "puo contenere soia",
    "può contenere senape",
    "puo contenere senape",
    "frammenti di nocciolo",
    "frutta a guscio",
    "frutta secca",
    "noci pecan",
    "noci macadamia",
    "noci del brasile",
]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        chunks: list[str] = []
        for child in value.values():
            chunks.append(normalize_text(child))
        return " ".join(chunks)
    if isinstance(value, list):
        return " ".join(normalize_text(item) for item in value)
    return str(value)


def product_text(product: dict[str, Any]) -> str:
    values = [
        product.get("name", ""),
        product.get("shortDescr", ""),
        product.get("description", ""),
        product.get("searchable_text", ""),
        product.get("metaData", ""),
        product.get("ALLERGEN_OTHER", ""),
        product.get("ALLERGEN_CONTAINS", ""),
        product.get("INGREDIENTS_OTHER", ""),
    ]
    text = " ".join(normalize_text(v) for v in values)
    return text.lower()


def _match_any(patterns: list[str], text: str) -> bool:
    return any(pattern in text for pattern in patterns)


def find_safe_examples(products: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for product in products:
        text = product_text(product)
        if _match_any(SAFE_PATTERNS, text) and not _match_any(EU_NUT_PATTERNS, text):
            examples.append({
                "productId": product.get("productId"),
                "name": product.get("name"),
                "vendor": product.get("vendor"),
                "why": "EU label wording: no nuts / no gluten claim",
                "snippet": re.sub(r"<.*?>", " ", text)[:500],
            })
        if len(examples) >= limit:
            break
    return examples


def find_nut_examples(products: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for product in products:
        text = product_text(product)
        if _match_any(EU_NUT_PATTERNS, text):
            examples.append({
                "productId": product.get("productId"),
                "name": product.get("name"),
                "vendor": product.get("vendor"),
                "why": "EU label wording: may contain nuts / shell-fruit allergens",
                "snippet": re.sub(r"<.*?>", " ", text)[:500],
            })
        if len(examples) >= limit:
            break
    return examples


def main() -> None:
    with SOURCE_PATH.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    products = payload.get("products", [])
    examples = {
        "safe_examples": find_safe_examples(products, limit=5),
        "nut_examples": find_nut_examples(products, limit=5),
    }

    OUTPUT_PATH.write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = ["category", "productId", "name", "vendor", "why", "snippet"]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for label, rows in [("safe", examples["safe_examples"]), ("nut", examples["nut_examples"])]:
            for row in rows:
                writer.writerow({
                    "category": label,
                    "productId": row.get("productId"),
                    "name": row.get("name"),
                    "vendor": row.get("vendor"),
                    "why": row.get("why"),
                    "snippet": row.get("snippet"),
                })

    print(f"Wrote {OUTPUT_PATH}")
    print(f"Wrote {CSV_PATH}")
    print(json.dumps(examples, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
