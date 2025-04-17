# OpenClash AdGuard

This repository provides an AdBlock list formatted for OpenClash. The source is taken from [AdGuard Hostlists Registry](https://github.com/AdguardTeam/HostlistsRegistry) and is updated automatically every day using GitHub Actions.

![image](https://github.com/user-attachments/assets/d88a41d7-0e90-4be3-addb-09d0f47d1ae5)

## How to Use

To integrate this list with OpenClash, edit your `config.yaml` file located in `/etc/openclash/config/config.yaml` as follows:

```yaml
rule-providers:
  adguard:
    type: http
    behavior: classical
    path: "./rule_provider/adguard.yaml"
    url: https://raw.githubusercontent.com/AyraHikari/openclash_adguard/main/adguard_openclash.yaml
    interval: 43200 # Update rules every 12 hours

rules:
# AdGuard
- RULE-SET,adguard,REJECT
```

## Features
- Automatically updated every 12 hours with the latest AdGuard DNS filter.
- Formatted specifically for OpenClash compatibility.
- Includes support for exceptions and optimized formatting.

## Notes
- Commit & Apply OpenClash after modifying the `config.yaml` file to apply changes.

## License
This project uses data sourced from [AdGuard Hostlists Registry](https://github.com/AdguardTeam/HostlistsRegistry) and adheres to their licensing terms. For details, refer to their repository.
