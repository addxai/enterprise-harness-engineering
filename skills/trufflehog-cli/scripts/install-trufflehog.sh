#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
VERSION="$(tr -d '\r\n' < "$SKILL_DIR/assets/trufflehog-version.txt")"
INSTALL_DIR="${1:-$HOME/.local/bin}"
TMP_DIR="${TMPDIR:-/tmp}/trufflehog-install-$VERSION"
VERIFY_SIGNATURE="${TRUFFLEHOG_VERIFY_CHECKSUM_SIGNATURE:-1}"
ALLOW_REMOTE_CHECKSUM="${TRUFFLEHOG_ALLOW_REMOTE_CHECKSUM:-0}"

mkdir -p "$TMP_DIR" "$INSTALL_DIR"

case "$(uname -s)" in
  Darwin) OS="darwin" ;;
  Linux) OS="linux" ;;
  *)
    echo "Unsupported OS: $(uname -s)" >&2
    exit 1
    ;;
esac

case "$(uname -m)" in
  x86_64|amd64) ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *)
    echo "Unsupported architecture: $(uname -m)" >&2
    exit 1
    ;;
esac

TARBALL="trufflehog_${VERSION}_${OS}_${ARCH}.tar.gz"
BASE_URL="https://github.com/trufflesecurity/trufflehog/releases/download/v${VERSION}"
ARCHIVE_PATH="$TMP_DIR/$TARBALL"
LOCAL_CHECKSUM_PATH="$SKILL_DIR/checksums/trufflehog-${VERSION}-sha256.txt"
CHECKSUM_PATH="$TMP_DIR/checksums.txt"
REMOTE_CHECKSUM_FILE="trufflehog_${VERSION}_checksums.txt"
REMOTE_CHECKSUM_PATH="$TMP_DIR/$REMOTE_CHECKSUM_FILE"
REMOTE_SIG_PATH="$TMP_DIR/${REMOTE_CHECKSUM_FILE}.sig"
REMOTE_PEM_PATH="$TMP_DIR/${REMOTE_CHECKSUM_FILE}.pem"

curl -fsSL -o "$ARCHIVE_PATH" "$BASE_URL/$TARBALL"

if [ -f "$LOCAL_CHECKSUM_PATH" ]; then
  cp "$LOCAL_CHECKSUM_PATH" "$CHECKSUM_PATH"
elif [ "$ALLOW_REMOTE_CHECKSUM" = "1" ]; then
  curl -fsSL -o "$CHECKSUM_PATH" "$BASE_URL/trufflehog_${VERSION}_checksums.txt"
else
  echo "Missing local checksum file: $LOCAL_CHECKSUM_PATH" >&2
  echo "Refusing remote checksum fetch by default." >&2
  echo "Set TRUFFLEHOG_ALLOW_REMOTE_CHECKSUM=1 to allow remote fallback." >&2
  exit 1
fi

if [ "$VERIFY_SIGNATURE" = "1" ]; then
  if command -v cosign >/dev/null 2>&1; then
    curl -fsSL -o "$REMOTE_CHECKSUM_PATH" "$BASE_URL/$REMOTE_CHECKSUM_FILE"
    curl -fsSL -o "$REMOTE_SIG_PATH" "$BASE_URL/${REMOTE_CHECKSUM_FILE}.sig"
    curl -fsSL -o "$REMOTE_PEM_PATH" "$BASE_URL/${REMOTE_CHECKSUM_FILE}.pem"

    cosign verify-blob "$REMOTE_CHECKSUM_PATH" \
      --certificate "$REMOTE_PEM_PATH" \
      --signature "$REMOTE_SIG_PATH" \
      --certificate-identity-regexp 'https://github\.com/trufflesecurity/trufflehog/\.github/workflows/.+' \
      --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
      >/dev/null
    if [ ! -f "$LOCAL_CHECKSUM_PATH" ] && [ "$ALLOW_REMOTE_CHECKSUM" = "1" ]; then
      cp "$REMOTE_CHECKSUM_PATH" "$CHECKSUM_PATH"
    fi
  else
    echo "WARNING: cosign not found; skipped checksum signature verification." >&2
    echo "Install cosign or set TRUFFLEHOG_VERIFY_CHECKSUM_SIGNATURE=0 to silence this warning." >&2
  fi
fi

EXPECTED_HASH="$(awk -v file="$TARBALL" '$2 == file { print $1 }' "$CHECKSUM_PATH")"
if [ -z "$EXPECTED_HASH" ]; then
  echo "Failed to find checksum for $TARBALL" >&2
  exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL_HASH="$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
  ACTUAL_HASH="$(shasum -a 256 "$ARCHIVE_PATH" | awk '{print $1}')"
else
  ACTUAL_HASH="$(openssl dgst -sha256 "$ARCHIVE_PATH" | awk '{print $NF}')"
fi

if [ "$EXPECTED_HASH" != "$ACTUAL_HASH" ]; then
  echo "SHA256 mismatch for $TARBALL" >&2
  exit 1
fi

tar -xzf "$ARCHIVE_PATH" -C "$TMP_DIR" trufflehog
install -m 0755 "$TMP_DIR/trufflehog" "$INSTALL_DIR/trufflehog"

printf 'Installed trufflehog %s to %s\n' "$VERSION" "$INSTALL_DIR"
