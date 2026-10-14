#!/usr/bin/env python3
"""Detect real nut allergen warnings without counting generic gluten warnings."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

NUT_TERMS = [
    "arachidi",
    "anacardi",
    "mandorle",
    "mandorla",
    "nocciole",
    "nocciola",
    "noci",
    "nocciolo",
    "noccioli",
    "pistacchi",
    "pistacchio",
    "noci pecan",
    "noci macadamia",
    "noci del brasile",
    "frutta a guscio",
    "frutta secca",
]

GENERIC_WARNING_PREFIXES = (
    "può contenere",
    "puo contenere",
    "potrebbe contenere",
    "può contenere tracce di",
    "puo contenere tracce di",
)

NUT_REGEX = re.compile(
    r"(?:arachidi|anacardi|mandorle|mandorla|nocciole|nocciola|noci|nocciolo|noccioli|pistacchi|pistacchio|noci pecan|noci macadamia|noci del brasile|frutta a guscio|frutta secca)",
    flags=re.IGNORECASE,
)

CONTAINS_NUTS_REGEX = re.compile(
    r"(?:\bcontiene\b|\bcontengono\b)[^.;\n]*?(?:arachidi|anacardi|mandorle|mandorla|nocciole|nocciola|noci|nocciolo|noccioli|pistacchi|pistacchio|noci pecan|noci macadamia|noci del brasile|frutta a guscio|frutta secca)",
    flags=re.IGNORECASE,
)

MAY_CONTAIN_NUTS_REGEX = re.compile(
    r"(?:pu(?:ò|o) contenere|potrebbe contenere)(?:[^.;\n]*?)(?:arachidi|anacardi|mandorle|mandorla|nocciole|nocciola|noci|nocciolo|noccioli|pistacchi|pistacchio|noci pecan|noci macadamia|noci del brasile|frutta a guscio|frutta secca)",
    flags=re.IGNORECASE,
)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(normalize_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(normalize_text(v) for v in value)
    return str(value)


def _find_matches(text: str, regex: re.Pattern[str]) -> list[str]:
    return [match.group(0).strip().lower() for match in regex.finditer(text)]


def detect_nut_flags(text: str) -> dict[str, Any]:
    lower_text = text.lower()
    matched_terms: list[str] = []
    for term in sorted(NUT_TERMS, key=len, reverse=True):
        if term in lower_text and term not in matched_terms:
            matched_terms.append(term)

    direct_matches = _find_matches(lower_text, CONTAINS_NUTS_REGEX)
    may_matches = _find_matches(lower_text, MAY_CONTAIN_NUTS_REGEX)

    explicit_allergen_phrases = []
    for phrase in direct_matches + may_matches:
        if phrase and phrase not in explicit_allergen_phrases:
            explicit_allergen_phrases.append(phrase)

    contains_nuts = bool(direct_matches)
    may_contain_nuts = bool(may_matches)

    allergen_flags: list[str] = []
    if contains_nuts or may_contain_nuts:
        allergen_flags.append("nuts")

    return {
        "allergen_terms": matched_terms,
        "allergen_flags": allergen_flags,
        "contains_nuts": contains_nuts,
        "may_contain_nuts": may_contain_nuts,
        "explicit_allergen_phrases": explicit_allergen_phrases,
    }


def update_product(product: dict[str, Any]) -> dict[str, Any]:
    text_parts = [
        product.get("allergen_text") or "",
        product.get("searchable_text") or "",
        product.get("name") or "",
        product.get("description") or "",
        product.get("shortDescr") or "",
    ]
    detection = detect_nut_flags(" ".join(normalize_text(part) for part in text_parts))
    product["allergen_terms"] = detection["allergen_terms"]
    product["allergen_flags"] = detection["allergen_flags"]
    product["contains_nuts"] = detection["contains_nuts"]
    product["may_contain_nuts"] = detection["may_contain_nuts"]
    product["explicit_allergen_phrases"] = detection["explicit_allergen_phrases"]
    return product


def update_products_file(path: Path) -> int:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    products = payload.get("products") if isinstance(payload, dict) else payload
    if not isinstance(products, list):
        raise ValueError(f"{path} does not contain a product list")

    updated = [update_product(product) for product in products]
    payload["products"] = updated if isinstance(payload, dict) else updated
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    return len(updated)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "products.json", help="Path to the canonical products JSON file")
    args = parser.parse_args()

    updated_count = update_products_file(args.input)
    print(f"Updated {updated_count} products in {args.input}")


if __name__ == "__main__":
    main()
