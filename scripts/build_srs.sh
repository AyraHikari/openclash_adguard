#!/bin/sh
# Compile sing-box rule-set JSON into binary .srs with a pinned sing-box.
#
# The router loads .srs directly and never compiles: that needs ~1.5 GB and the
# device has 441 MB, so the compile happens here, on an x86 host, with the same
# sing-box release the router runs.
#
# Usage:
#   scripts/convert_adguard_to_singbox.py            # write rules/*.json
#   scripts/build_srs.sh [outdir]                    # write rules/*.srs
#
# Environment:
#   SINGBOX_VERSION  sing-box release tag (default 1.13.21)
#   SINGBOX_CACHE    download cache dir (default ./.cache/singbox)
set -eu

VER="${SINGBOX_VERSION:-1.13.21}"
OUT="${1:-rules}"
CACHE="${SINGBOX_CACHE:-.cache/singbox}"

case "$(uname -m)" in
	x86_64 | amd64) MACH=amd64 ;;
	aarch64 | arm64) MACH=arm64 ;;
	*) echo "unsupported host arch: $(uname -m)" >&2; exit 1 ;;
esac

case "$(uname -s)" in
	Linux) OS=linux ;;
	Darwin) OS=darwin ;;
	*) echo "unsupported host os: $(uname -s)" >&2; exit 1 ;;
esac

SB="$CACHE/sing-box-$VER-$OS-$MACH/sing-box"
if [ ! -x "$SB" ]; then
	mkdir -p "$CACHE"
	url="https://github.com/SagerNet/sing-box/releases/download/v$VER/sing-box-$VER-$OS-$MACH.tar.gz"
	echo "Downloading $url"
	curl -fsSL -o "$CACHE/sing-box-$VER-$OS-$MACH.tar.gz" "$url"
	tar -xzf "$CACHE/sing-box-$VER-$OS-$MACH.tar.gz" -C "$CACHE"
fi
"$SB" version | head -1

for name in allow block; do
	src="$OUT/adguard_$name.json"
	dst="$OUT/adguard_$name.srs"
	[ -f "$src" ] || { echo "missing $src" >&2; exit 1; }
	"$SB" rule-set compile -o "$dst" "$src"
	printf '%s: %s bytes\n' "$dst" "$(wc -c < "$dst")"
done
