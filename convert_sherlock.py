#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request
import sys
from pathlib import Path

SHERLOCK_URL = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json"
OUTPUT = Path(__file__).parent / "data" / "sites.json"

CATEGORY_MAP = {
    "social": "social", "gaming": "gaming", "music": "music",
    "video": "video", "coding": "coding", "blog": "blog",
    "adult": "misc", "art": "art", "news": "news",
    "shopping": "shopping", "sport": "sport", "education": "education",
    "crypto": "crypto", "forum": "forum", "dating": "dating",
    "professional": "professional",
}

def download_sherlock():
    print("[>] Téléchargement Sherlock...")
    req = urllib.request.Request(SHERLOCK_URL, headers={"User-Agent": "FasoOSINT/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def convert(name, info):
    if not isinstance(info, dict):
        return None
    url = info.get("url", info.get("url_probe", ""))
    if not url:
        return None
    url = url.replace("{}", "{username}")
    etype = info.get("errorType", "status_code")
    if etype == "message":
        emsg = info.get("errorMsg", "")
        if isinstance(emsg, list):
            emsg = emsg[0] if emsg else ""
    else:
        etype = "status_code"
        emsg = ""
    cat = CATEGORY_MAP.get((info.get("category") or "").lower(), "misc")
    return {"name": name, "url": url, "error_type": etype,
            "error_msg": emsg, "category": cat, "region": "global"}

def load_existing():
    if OUTPUT.exists():
        with open(OUTPUT, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def merge(existing, new_sites):
    names = {s["name"].lower() for s in existing}
    urls  = {s["url"].split("{username}")[0].lower() for s in existing}
    added = 0
    result = list(existing)
    for s in new_sites:
        nk = s["name"].lower()
        uk = s["url"].split("{username}")[0].lower()
        if nk not in names and uk not in urls:
            result.append(s)
            names.add(nk)
            urls.add(uk)
            added += 1
    return result, added

def main():
    data = download_sherlock()
    print(f"[✅] {len(data)} sites Sherlock téléchargés")

    converted = []
    for name, info in data.items():
        site = convert(name, info)
        if site:
            converted.append(site)
    print(f"[>] Convertis : {len(converted)}")

    existing = load_existing()
    print(f"[>] Existants : {len(existing)}")

    final, added = merge(existing, converted)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"\n[★] Ajoutés   : {added}")
    print(f"[★] Total final: {len(final)}")
    print(f"[✅] Sauvegardé → {OUTPUT}")

if __name__ == "__main__":
    main()
