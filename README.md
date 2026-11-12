# OpenClash AdGuard (AdGuard & EasyList Converter)

This repository provides **OpenClash-compatible rule-providers** converted from **AdGuard / Adblock (ABP) format lists** into **Clash classical YAML**.

The lists are automatically fetched, parsed, deduplicated, and converted every **12 hours** using **GitHub Actions**.

Sources include **AdGuard Hostlists Registry** and **EasyList anti-adblock filters**.

<p align="center">
  <img src="https://github.com/user-attachments/assets/e6ccfa53-99ac-45df-9cb6-d5fb0f44e00f"/>
</p>

---

## What This Repo Provides

This repository generates **two separate rule-providers**:

| File | Purpose |
|----|----|
| `adguard_block.yaml` | Main blocking rules (REJECT) |
| `adguard_allow.yaml` | Exception / whitelist rules (DIRECT) |

> ⚠️ Important:  
> OpenClash **cannot apply exceptions inside a single ruleset**.  
> Therefore, **allow rules must be applied BEFORE block rules**.

---

## Rule Sources

The following upstream lists are used:

- AdGuard Base Filter  
- AdGuard Mobile Ads  
- AdGuard Tracking Protection  
- AdGuard Mobile Tracking  
- AdGuard Social Media  
- AdGuard Annoyances  
- AdGuard Spyware  
- EasyList Anti-Adblock Filters  

All sources are automatically merged, normalized, and deduplicated.

---

## How to Use with OpenClash

Edit your OpenClash config file: /etc/openclash/config/config.yaml


### 1️⃣ Add Rule Providers

```yaml
rule-providers:
  adguard_allow:
    type: http
    behavior: classical
    path: ./ruleset/adguard_allow.yaml
    url: https://raw.githubusercontent.com/AyraHikari/openclash_adguard/main/rules/adguard_allow.yaml
    interval: 43200

  adguard_block:
    type: http
    behavior: classical
    path: ./ruleset/adguard_block.yaml
    url: https://raw.githubusercontent.com/AyraHikari/openclash_adguard/main/rules/adguard_block.yaml
    interval: 43200
```

### 2️⃣ Apply Rules (Order Matters!)

```yaml
rules:
  # AdGuard Allow (Exceptions FIRST)
  - RULE-SET,adguard_allow,DIRECT

  # AdGuard Block
  - RULE-SET,adguard_block,REJECT
```

## Features

- ✅ Automatically updated every 12 hours

- ✅ Proper AdGuard / ABP parser (not regex-only)

- ✅ Supports:

  - ||domain^

  - @@||domain^ (exceptions)

  - Hosts format (0.0.0.0 domain)

- ✅ Global deduplication

- ✅ Invalid rules, IPs, paths, and options are safely ignored

- ✅ Optimized for OpenClash stability & performance

## Recommended Usage Notes

- Always place allow rules before block rules

- Use Commit & Apply in OpenClash after updating config

- Works best with Global / Rule-based mode

- Suitable for:

  - DNS-level ad blocking

  - Tracking protection

  - Anti-adblock bypass

  - Lightweight router deployments

## Update Schedule

- ⏱ Every 12 hours via GitHub Actions

- 🔁 Manual trigger supported via workflow dispatch

## sing-box rule-sets (`.srs`)

Binary [sing-box rule-sets](https://sing-box.sagernet.org/configuration/rule-set/) are built from the same
sources by `scripts/convert_adguard_to_singbox.py` and compiled with a pinned sing-box release
(`1.13.21`, the version OpenWrt's `sing-box-tiny` ships) by `scripts/build_srs.sh`.

They are published to the **`srs`** branch, force-pushed on every run so the raw URL stays stable and
the git history does not grow:

| File | Purpose |
|----|----|
| `adguard_block.srs` | Block list, mount as `REJECT` / `block` |
| `adguard_allow.srs` | Exceptions, route `DIRECT` **before** the block rule |
| `meta.json` | sing-box version, domain counts, size and sha256 of both files |

```
https://raw.githubusercontent.com/AyraHikari/openclash_adguard/srs/adguard_block.srs
https://raw.githubusercontent.com/AyraHikari/openclash_adguard/srs/adguard_allow.srs
https://raw.githubusercontent.com/AyraHikari/openclash_adguard/srs/meta.json
```

### sing-box / Momo usage

Do **not** use `format: "source"` on a router: sing-box would compile the 300k-domain list in RAM
(~1.5 GB needed, most routers have far less). Use the precompiled binary with `format: "binary"`.

```json
"rule_set": [
  {
    "type": "remote",
    "tag": "adguard-block",
    "format": "binary",
    "url": "https://raw.githubusercontent.com/AyraHikari/openclash_adguard/srs/adguard_block.srs",
    "download_detour": "DIRECT",
    "update_interval": "12h"
  }
],
"route": {
  "rules": [
    { "action": "sniff" },
    { "rule_set": "adguard-allow", "action": "route", "outbound": "DIRECT" },
    { "rule_set": "adguard-block", "action": "route", "outbound": "BLOCK" }
  ]
}
```

`download_detour` must be a direct outbound, otherwise the download itself is routed through the
proxy that is being configured.

### Local build

```sh
python3 scripts/convert_adguard_to_singbox.py      # rules/*.json
SINGBOX_VERSION=1.13.21 scripts/build_srs.sh rules # rules/*.srs
```

`.srs` files are only loadable by a sing-box release whose rule-set format is compatible: rebuild when
the router's sing-box version changes.

## License & Attribution

This project does not create new blocklists.

All data is sourced from:

- https://github.com/AdguardTeam/HostlistsRegistry

- https://easylist.to

Please refer to the original repositories for licensing terms.

## Disclaimer

This project is intended for personal and educational use.
Blocking effectiveness depends on rule order, OpenClash mode, and DNS behavior.
