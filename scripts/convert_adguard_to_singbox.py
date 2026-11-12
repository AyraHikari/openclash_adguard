#!/usr/bin/env python3
"""Convert AdGuard / ABP lists into sing-box rule-set source JSON.

The JSON is what `sing-box rule-set compile` turns into a binary `.srs`. The
router loads the compiled form directly, so it never compiles the block list
itself: that needs ~1.5 GB and the device has 441 MB.

Compile on an x86 host with the same sing-box release the router runs, then
publish the `.srs` (see the "sing-box" section in README.md).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convert_adguard_to_openclash import DEFAULT_SOURCES, collect_domains


def build_rule_set(domains: list[str]) -> dict:
    rules = [{"domain_suffix": domains}] if domains else []
    return {"version": 3, "rules": rules}


def write_json(path: str, payload: dict) -> int:
    count = 0
    if payload["rules"]:
        count = len(payload["rules"][0].get("domain_suffix", []))
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"Wrote: {path} ({count} domains)")
    return count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", help="Source list URL (repeatable, defaults to DEFAULT_SOURCES)")
    ap.add_argument("--out-block", default="rules/adguard_block.json")
    ap.add_argument("--out-allow", default="rules/adguard_allow.json")
    args = ap.parse_args()

    block_domains, allow_domains = collect_domains(args.url or DEFAULT_SOURCES)
    write_json(args.out_block, build_rule_set(block_domains))
    write_json(args.out_allow, build_rule_set(allow_domains))
    return 0


if __name__ == "__main__":
    sys.exit(main())
