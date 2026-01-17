#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import re
import sys
from urllib.request import urlopen, Request

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$"
)

def is_ip(s: str) -> bool:
    # very small IP check; good enough to skip obvious IPs
    if ":" in s:  # ipv6
        return True
    parts = s.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False

def normalize_domain(d: str) -> str | None:
    d = d.strip().lower()
    if not d:
        return None
    # strip leading wildcard dots
    d = d.lstrip(".")
    # strip possible trailing dot
    d = d.rstrip(".")
    if is_ip(d):
        return None
    if DOMAIN_RE.match(d):
        return d
    return None

def extract_from_hosts(line: str) -> list[str]:
    # e.g. "0.0.0.0 example.com" or "127.0.0.1 example.com"
    parts = line.split()
    if len(parts) < 2:
        return []
    if is_ip(parts[0]):
        dom = normalize_domain(parts[1])
        return [dom] if dom else []
    return []

def strip_inline_comment(line: str) -> str:
    # host lists sometimes have: "0.0.0.0 domain # comment"
    if "#" in line:
        line = line.split("#", 1)[0]
    return line.strip()

def clean_abp_rule(rule: str) -> str:
    # remove options: $...
    rule = rule.split("$", 1)[0]
    # remove path: /...
    rule = rule.split("/", 1)[0]
    return rule.strip()

def extract_from_abp(line: str) -> tuple[list[str], list[str]]:
    """
    Returns (block_domains, allow_domains)
    Supports:
      ||example.com^
      @@||example.com^
      |http://example.com^ (we ignore these mostly)
    """
    block: list[str] = []
    allow: list[str] = []

    raw = line.strip()
    if not raw or raw.startswith(("!", "[")):
        return block, allow

    raw = clean_abp_rule(raw)

    is_exception = raw.startswith("@@")
    if is_exception:
        raw = raw[2:].lstrip()

    # Most valuable pattern for domain-based blocking:
    # ||example.com^
    if raw.startswith("||"):
        raw = raw[2:]
        # end anchor marker ^
        raw = raw.split("^", 1)[0]
        raw = raw.strip()
        dom = normalize_domain(raw)
        if dom:
            (allow if is_exception else block).append(dom)
        return block, allow

    # Also accept plain domains in some lists (rare, but happens)
    dom = normalize_domain(raw)
    if dom:
        (allow if is_exception else block).append(dom)

    return block, allow

def fetch_text(url: str, timeout: int = 60) -> str:
    req = Request(url, headers={"User-Agent": "openclash-adguard-converter/1.0"})
    with urlopen(req, timeout=timeout) as r:
        data = r.read()
    # try utf-8, fallback latin-1
    try:
        return data.decode("utf-8", errors="replace")
    except Exception:
        return data.decode("latin-1", errors="replace")

def write_yaml(path: str, header_lines: list[str], domains: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for h in header_lines:
            f.write(h.rstrip() + "\n")
        f.write("payload:\n")
        for d in domains:
            # Safer default: DOMAIN-SUFFIX
            f.write(f"  - DOMAIN-SUFFIX,{d}\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", required=True, help="Source list URL (repeatable)")
    ap.add_argument("--out-block", default="rules/adguard_block.yaml")
    ap.add_argument("--out-allow", default="rules/adguard_allow.yaml")
    ap.add_argument("--repo", default="https://github.com/AyraHikari/openclash_adguard")
    args = ap.parse_args()

    block_set: set[str] = set()
    allow_set: set[str] = set()

    for url in args.url:
        text = fetch_text(url)
        for line in text.splitlines():
            line = strip_inline_comment(line)
            if not line:
                continue

            # hosts format
            for d in extract_from_hosts(line):
                if d:
                    block_set.add(d)

            # abp/adguard format
            b, a = extract_from_abp(line)
            for d in b:
                block_set.add(d)
            for d in a:
                allow_set.add(d)

    # If a domain appears in allowlist, remove it from blocklist.
    block_set.difference_update(allow_set)

    now = dt.datetime.now(dt.timezone.utc).astimezone()
    stamp = now.strftime("%Y-%m-%d %H:%M:%S %z")

    sources = "\n".join([f"# - {u}" for u in args.url])

    header_common = [
        f"# OpenClash AdGuard Converted: {args.repo}",
        f"# Updated at: {stamp}",
        "# Sources:",
        sources,
        "",
    ]

    block_domains = sorted(block_set)
    allow_domains = sorted(allow_set)

    write_yaml(args.out_block, header_common + [f"# Total block domains: {len(block_domains)}", ""], block_domains)
    write_yaml(args.out_allow, header_common + [f"# Total allow domains: {len(allow_domains)}", ""], allow_domains)

    print(f"Wrote:\n- {args.out_block} ({len(block_domains)} domains)\n- {args.out_allow} ({len(allow_domains)} domains)")

if __name__ == "__main__":
    sys.exit(main())
