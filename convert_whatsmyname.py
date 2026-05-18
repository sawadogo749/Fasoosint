#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_whatsmyname.py — FasoOSINT
Télécharge la base WhatsMyName (500+ sites dont Facebook, Instagram, TikTok)
et la convertit au format FasoOSINT sites.json
"""

import json
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
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
    "dating": "dating",
    "crypto": "crypto",
    "forum": "forum",
    "photo": "art",
    "business": "professional",
    "finance": "professional",
    "tech": "coding",
}

def download():
    print("[>] Téléchargement base WhatsMyName...")
    req = urllib.request.Request(URL, headers={"User-Agent": "FasoOSINT/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def convert(site):
    if not isinstance(site, dict):
        return None

    name = site.get("name", "")
    uri = site.get("uri_check", "")
    if not uri or not name:
        return None

    # Normalise placeholder
    uri = uri.replace("{account}", "{username}")
    if "{username}" not in uri:
        return None

    # Detection
    e_code = site.get("e_code", 200)
    e_string = site.get("e_string", "")
    m_string = site.get("m_string", "")

    if m_string:
        error_type = "message"
        error_msg = m_string
    elif e_code == 200:
        error_type = "status_code"
        error_msg = ""
    else:
        error_type = "status_code"
        error_msg = ""

    cat_raw = (site.get("category") or "").lower()
    category = CATEGORY_MAP.get(cat_raw, "misc")

    return {
        "name": name,
        "url": uri,
        "error_type": error_type,
        "error_msg": error_msg,
        "category": category,
        "region": "global"
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
    data = download()
    sites_raw = data.get("sites", [])
    print(f"[✅] {len(sites_raw)} sites WhatsMyName téléchargés")

    converted = []
    for site in sites_raw:
        s = convert(site)
        if s:
            converted.append(s)
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
