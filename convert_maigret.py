#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_maigret.py — FasoOSINT
Télécharge la base Maigret (3000+ sites) et la convertit
au format FasoOSINT sites.json
"""

import json
import urllib.request
from pathlib import Path

MAIGRET_URL = "https://raw.githubusercontent.com/soxoj/maigret/main/maigret/resources/data.json"
OUTPUT = Path(__file__).parent / "data" / "sites.json"

CATEGORY_MAP = {
    "social": "social",
    "gaming": "gaming",
    "music": "music",
    "video": "video",
    "coding": "coding",
    "blog": "blog",
    "adult": "misc",
    "art": "art",
    "news": "news",
    "shopping": "shopping",
    "sport": "sport",
    "education": "education",
    "crypto": "crypto",
    "forum": "forum",
    "dating": "dating",
    "professional": "professional",
    "photo": "art",
    "finance": "professional",
    "tech": "coding",
    "travel": "misc",
    "food": "misc",
    "health": "misc",
    "business": "professional",
}

def download_maigret():
    print("[>] Téléchargement base Maigret...")
    req = urllib.request.Request(MAIGRET_URL, headers={"User-Agent": "FasoOSINT/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def convert(name, info):
    if not isinstance(info, dict):
        return None

    # URL de profil
    url = info.get("url", "")
    if not url:
        return None

    # Normalise placeholder
    url = url.replace("{}", "{username}")
    if "{username}" not in url:
        return None

    # error_type
    error_type_raw = info.get("errorType", "status_code")
    if error_type_raw == "message":
        error_type = "message"
        emsg = info.get("errorMsg", "")
        if isinstance(emsg, list):
            emsg = emsg[0] if emsg else ""
        if isinstance(emsg, dict):
            emsg = str(list(emsg.values())[0]) if emsg else ""
    elif error_type_raw == "status_code":
        error_type = "status_code"
        emsg = ""
    else:
        error_type = "status_code"
        emsg = ""

    # Catégorie
    raw_cat = (info.get("category") or info.get("tags", [""])[0] if info.get("tags") else "").lower()
    category = CATEGORY_MAP.get(raw_cat, "misc")

    # Région
    tags = info.get("tags", [])
    region = "africa" if any(t in ["africa","african","burkina","nigeria","kenya","ghana","senegal","cameroon"] for t in tags) else "global"

    return {
        "name": name,
        "url": url,
        "error_type": error_type,
        "error_msg": emsg,
        "category": category,
        "region": region
    }

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
    data = download_maigret()
    print(f"[✅] {len(data)} sites Maigret téléchargés")

    converted = []
    for name, info in data.items():
        site = convert(name, info)
        if site:
            converted.append(site)
    print(f"[>] Convertis : {len(converted)}")

    existing = load_existing()
    print(f"[>] Existants FasoOSINT : {len(existing)}")

    final, added = merge(existing, converted)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"\n[★] Ajoutés   : {added}")
    print(f"[★] Total final: {len(final)}")
    print(f"[✅] Sauvegardé → {OUTPUT}")

if __name__ == "__main__":
    main()
