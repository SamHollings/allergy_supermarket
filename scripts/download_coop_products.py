#!/usr/bin/env python3
"""Download a detailed Coop Shop product dataset into a single canonical JSON file."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BASE_URL = "https://www.coopshop.it/ebsn/api/products"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
}


def flatten_value(value: Any, prefix: str = "") -> list[str]:
    values: list[str] = []
    if value is None:
        return values
    if isinstance(value, str):
        cleaned = " ".join(value.strip().split())
        if cleaned:
            values.append(cleaned)
        return values
    if isinstance(value, (int, float, bool)):
        values.append(str(value))
        return values
    if isinstance(value, dict):
        for key, nested in value.items():
            next_prefix = f"{prefix} {key}" if prefix else str(key)
            values.extend(flatten_value(nested, next_prefix))
        return values
    if isinstance(value, list):
        for item in value:
            values.extend(flatten_value(item, prefix))
        return values
    return values


def fetch_page(page: int, page_size: int) -> dict[str, Any]:
    response = requests.get(
        BASE_URL,
        params={"page": page, "page_size": page_size, "details": True},
        headers=DEFAULT_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def build_product_record(product: dict[str, Any]) -> dict[str, Any]:
    text_parts: list[str] = []
    for key in ["name", "shortDescr", "description", "slug", "vendor", "metaData", "productInfos", "breadCrumbs"]:
        if key in product:
            text_parts.extend(flatten_value(product.get(key)))
    searchable_text = " ".join(text_parts)

    product_record = dict(product)
    product_record["searchable_text"] = searchable_text
    product_record["allergen_text"] = " ".join(
        flatten_value(product.get("metaData"))
    )
    product_record["downloaded_at"] = datetime.now(timezone.utc).isoformat()
    return product_record


def iter_products(max_items: int = 200, page_size: int = 24) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    page = 1
    metadata: dict[str, Any] = {}

    while len(collected) < max_items:
        payload = fetch_page(page, page_size)
        data = payload.get("data", {})
        products = data.get("products") or []
        metadata = data.get("page", {})

        if not products:
            break

        for product in products:
            if len(collected) >= max_items:
                break
            collected.append(build_product_record(product))

        if metadata.get("totPages") and page >= int(metadata.get("totPages")):
            break
        page += 1

    return collected, metadata


def save_products(products: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump({"products": products}, fh, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-items", type=int, default=200, help="Maximum number of products to fetch")
    parser.add_argument("--page-size", type=int, default=24, help="Products per page")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "products.json", help="Path for the canonical product export")
    args = parser.parse_args()

    products, metadata = iter_products(max_items=args.max_items, page_size=args.page_size)
    save_products(products, args.output)

    print(f"Saved {len(products)} product records to {args.output}")
    print(f"Metadata: {metadata}")


if __name__ == "__main__":
    main()
