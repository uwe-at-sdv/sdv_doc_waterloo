#!/bin/bash

# 1. Infos aus package.json extrahieren (benötigt node/npm)
PUBLISHER=$(node -pe "require('./package.json').publisher")
EXT_NAME=$(node -pe "require('./package.json').name")
VERSION=$(node -pe "require('./package.json').version")

ID="${PUBLISHER}.${EXT_NAME}"
IMG_DIR="img"

echo "ID:" ${ID}

# Ordner erstellen, falls nicht vorhanden
mkdir -p $IMG_DIR

echo "Erstelle Badges fuer $ID (v$VERSION)..."

# 2. Versions-Badge (Statisch)
curl -L "https://shields.io/badge/version-${VERSION}-blue.svg" | rsvg-convert -z 3 -f png -o "${IMG_DIR}/badge-version.png"

# 3. Download-Statistik (Dynamisch vom Marketplace)
# Shields.io nutzt hierfuer: /visual-studio-marketplace/d/:extensionId
curl -L "https://shields.io/vscode-marketplace/d/${ID}.svg" | rsvg-convert -z 3 -f png -o "${IMG_DIR}/badge-downloads.png"
echo "Fertig! Bilder liegen in /$IMG_DIR"

