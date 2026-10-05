#!/usr/bin/env python3
"""Sanity-check feed.xml before it goes live on GitHub Pages."""
import re
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

IT = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
path = sys.argv[1] if len(sys.argv) > 1 else "feed.xml"
errors = []

try:
    channel = ET.parse(path).getroot().find("channel")
except ET.ParseError as e:
    sys.exit(f"{path}: invalid XML: {e}")

for tag in ("title", "description", IT + "author", IT + "image", IT + "category"):
    if channel.find(tag) is None:
        errors.append(f"channel: missing {tag.replace(IT, 'itunes:')}")
if not channel.findtext(f"{IT}owner/{IT}email"):
    errors.append("channel: missing itunes:owner/itunes:email")

guids, numbers = set(), set()
for item in channel.findall("item"):
    title = item.findtext("title") or "(no title)"
    def err(msg):
        errors.append(f"{title}: {msg}")

    guid = item.findtext("guid")
    if not guid:
        err("missing guid")
    elif guid in guids:
        err(f"duplicate guid {guid}")
    guids.add(guid)

    enc = item.find("enclosure")
    if enc is None:
        err("missing enclosure")
    else:
        if not enc.get("url", "").startswith("https://"):
            err("enclosure url must be https")
        if not enc.get("length", "").isdigit() or int(enc.get("length")) == 0:
            err("enclosure length must be the file size in bytes")
        if enc.get("type") != "audio/mpeg":
            err("enclosure type should be audio/mpeg")

    try:
        parsedate_to_datetime(item.findtext("pubDate") or "")
    except (TypeError, ValueError):
        err("missing or malformed pubDate")

    dur = item.findtext(IT + "duration") or ""
    if not re.fullmatch(r"\d+|(\d+:)?\d{1,2}:\d{2}", dur):
        err("missing or malformed itunes:duration")

    ep = item.findtext(IT + "episode")
    if ep is not None:
        if ep in numbers:
            err(f"duplicate itunes:episode {ep}")
        numbers.add(ep)

    # TTS spellings like "A I" / "G P T" should not leak into show notes.
    spelled = re.findall(r"\b(?:[A-Z] ){1,}[A-Z]\b", item.findtext("description") or "")
    if spelled:
        err(f"spelled-out acronyms in description: {sorted(set(spelled))}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"{path}: OK ({len(guids)} episodes)")
