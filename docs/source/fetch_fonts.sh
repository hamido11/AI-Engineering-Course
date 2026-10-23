#!/bin/sh
# Downloads the open-licensed (OFL) fonts used by the PDF into ./fonts
set -e
cd "$(dirname "$0")/fonts"
BASE="https://raw.githubusercontent.com/google/fonts/main/ofl"
for f in ibmplexserif/IBMPlexSerif-Regular ibmplexserif/IBMPlexSerif-Italic ibmplexserif/IBMPlexSerif-SemiBold ibmplexserif/IBMPlexSerif-Bold \
         ibmplexmono/IBMPlexMono-Regular ibmplexmono/IBMPlexMono-Medium ibmplexmono/IBMPlexMono-SemiBold; do
  out="$(basename "$f").ttf"
  [ -s "$out" ] || curl -fsSL -o "$out" "$BASE/$f.ttf"
done
for w in 400 500 600 700; do
  out="SpaceGrotesk-$w.ttf"
  [ -s "$out" ] && continue
  url=$(curl -fsSL -A "Mozilla/5.0" "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@$w" | grep -oE 'https://[^)]+\.ttf' | head -1)
  curl -fsSL -o "$out" "$url"
done
ls -la
