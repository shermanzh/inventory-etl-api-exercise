#!/usr/bin/env python3
"""Thin command-line entry point for the inventory ETL exercise."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from inventory_etl import api_client, config, duplicates, fetch, parse, transform, writer


def load_and_transform(args: argparse.Namespace) -> list[dict[str, str]]:
    _location, content = fetch.fetch_inventory_bytes(args.initial_html_url)

    if args.flow == "file":
        fetch.save_bytes(content, args.download_path)
        source_rows = parse.parse_file(args.download_path)
    else:
        source_rows = parse.parse_bytes(content)

    duplicate_ids = duplicates.find_duplicate_item_numbers(source_rows)
    return transform.transform_rows(source_rows, duplicate_ids)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("generate_csv", "upload", "list_uploads"),
        nargs="?",
        default="generate_csv",
    )
    parser.add_argument(
        "--flow",
        choices=("memory", "file"),
        default="memory",
        help="Parse bytes directly or save the download before parsing",
    )
    parser.add_argument("--initial-html-url", default=config.INITIAL_HTML_URL)
    parser.add_argument(
        "--download-path", type=Path, default=config.DEFAULT_DOWNLOAD_PATH
    )
    parser.add_argument("--output", type=Path, default=config.DEFAULT_OUTPUT_PATH)
    parser.add_argument("--api-base-url", default=config.DEFAULT_API_BASE_URL)
    return parser


def main() -> int:
    args = build_argument_parser().parse_args()
    try:
        if args.command == "list_uploads":
            result = api_client.list_uploads(args.api_base_url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        rows = load_and_transform(args)
        if args.command == "generate_csv":
            writer.write_csv(rows, args.output)
            print(f"Wrote {len(rows)} rows to {args.output}")
            if args.flow == "file":
                print(f"Saved the S3 response to {args.download_path}")
        else:
            result = api_client.upload_inventory(args.api_base_url, rows)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, RuntimeError, ValueError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

