#!/usr/bin/env python3
"""Query the canonical Coop product dataset with allergen-aware filters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_products(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if isinstance(payload, dict):
        products = payload.get("products")
        if isinstance(products, list):
            return products
        return []
    if isinstance(payload, list):
        return payload
    return []


def product_vendor_name(product: dict[str, Any]) -> str:
    vendor = product.get("vendor")
    if isinstance(vendor, dict):
        return str(vendor.get("name") or "")
    if vendor is None:
        return str(product.get("vendor_name") or "")
    return str(vendor)


def product_category_name(product: dict[str, Any]) -> str:
    category = product.get("category")
    if category:
        return str(category)

    breadcrumbs = product.get("breadCrumbs")
    if isinstance(breadcrumbs, list) and breadcrumbs:
        last = breadcrumbs[-1]
        if isinstance(last, dict):
            return str(last.get("name") or "")
    return ""


def filter_products(
    products: list[dict[str, Any]],
    name_term: str | None = None,
    vendor: str | None = None,
    category: str | None = None,
    allergen: str | None = None,
    may_contain_nuts: bool = False,
    only_safe: bool = False,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for product in products:
        name = (product.get("name") or "").lower()
        text_blob = " ".join([
            name,
            str(product.get("shortDescr") or ""),
            str(product.get("description") or ""),
            str(product.get("searchable_text") or ""),
        ]).lower()
        vendor_name = product_vendor_name(product).lower()
        category_name = product_category_name(product).lower()

        if name_term and name_term.lower() not in text_blob:
            continue
        if vendor and vendor.lower() not in vendor_name:
            continue
        if category and category.lower() not in category_name:
            continue
        if allergen:
            field = f"contains_{allergen.lower()}"
            value = product.get(field)
            if value is not True:
                continue
        if may_contain_nuts and not bool(product.get("may_contain_nuts")):
            continue
        if only_safe:
            if bool(product.get("contains_nuts")) or bool(product.get("may_contain_nuts")):
                continue

        matches.append(product)
    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "products.json",
        help="Path to the canonical product JSON file",
    )
    parser.add_argument("--search", type=str, help="Case-insensitive substring to match in name or searchable text")
    parser.add_argument("--vendor", type=str, help="Case-insensitive vendor name filter")
    parser.add_argument("--category", type=str, help="Case-insensitive final category filter")
    parser.add_argument(
        "--allergen",
        choices=["nuts", "gluten", "soy", "milk", "eggs", "sesame", "mustard", "shellfish"],
        help="Return only products that contain this allergen flag",
    )
    parser.add_argument("--may-contain-nuts", action="store_true", help="Only show products with a may-contain-nuts warning")
    parser.add_argument("--safe-only", action="store_true", help="Return products without nuts or may-contain-nuts warnings")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of results to display")
    args = parser.parse_args()

    products = load_products(args.input)
    matches = filter_products(
        products,
        name_term=args.search,
        vendor=args.vendor,
        category=args.category,
        allergen=args.allergen,
        may_contain_nuts=args.may_contain_nuts,
        only_safe=args.safe_only,
    )

    print(f"Found {len(matches)} matching products")
    for product in matches[: args.limit]:
        vendor_name = product_vendor_name(product)
        category_name = product_category_name(product)
        nuts = product.get("contains_nuts")
        may_nuts = product.get("may_contain_nuts")
        print(
            f"{product.get('productId')} | {product.get('name')} | {vendor_name} | {category_name} "
            f"| nuts={nuts} | may_contain_nuts={may_nuts}"
        )


if __name__ == "__main__":
    main()
