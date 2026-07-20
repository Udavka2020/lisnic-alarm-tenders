#!/usr/bin/env python3
"""Fetch tenders from achizitii.md by CPV codes and output JSON."""

import urllib.request
import urllib.parse
import json
import re
import html
import sys
from datetime import datetime, timezone

CPV_LIST = {
    "32323500-8": "Video surveillance system",
    "32235000-9": "CCTV system",
    "35120000-1": "Surveillance and security systems",
    "45200000-9": "Construction works",
    "45310000-3": "Electrical installation",
    "35121000-8": "Security alarm system",
    "35121700-5": "Access control system",
    "32323000-1": "Video cameras",
    "32323100-2": "Colour video cameras",
    "32323200-3": "Video monitors",
    "32323300-4": "Video equipment",
    "42961100-1": "Access control system",
    "48730000-4": "Security software",
    "35111500-6": "Fire suppression system",
    "35111300-4": "Fire extinguishing equipment",
}

def search_cpv(cpv):
    """Search achizitii.md for tenders matching a CPV code."""
    params = urllib.parse.urlencode({"q": cpv, "limit": 5})
    url = f"https://achizitii.md/ro/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")

    results = []
    links = re.findall(r'<a[^>]*href="(/ro/public/announcement/[^"]+)"[^>]*>', body)
    titles = re.findall(
        r'<a[^>]*href="/ro/public/announcement/[^"]+"[^>]*>([^<]+)</a>', body
    )
    deadlines = re.findall(r"(\d{2}\.\d{2}\.\d{4}\s*\d{2}:\d{2})", body)

    for i, link in enumerate(links[:5]):
        title = html.unescape(titles[i].strip()) if i < len(titles) else ""
        deadline = deadlines[i] if i < len(deadlines) else ""
        results.append({
            "cpv": cpv,
            "category": CPV_LIST.get(cpv, cpv),
            "title": title,
            "url": f"https://achizitii.md{link}",
            "deadline": deadline,
            "found_at": datetime.now(timezone.utc).isoformat(),
        })
    return results


def main():
    cpv_filter = sys.argv[1].split(",") if len(sys.argv) > 1 else list(CPV_LIST.keys())

    all_results = []
    for cpv in cpv_filter[:5]:  # Limit to 5 per run for speed
        try:
            results = search_cpv(cpv)
            all_results.extend(results)
            print(f"  [{cpv}] {CPV_LIST.get(cpv, cpv)}: {len(results)} found", file=sys.stderr)
        except Exception as e:
            print(f"  [{cpv}] ERROR: {e}", file=sys.stderr)

    # Deduplicate by URL
    seen = set()
    unique = []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    print(json.dumps(unique, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
