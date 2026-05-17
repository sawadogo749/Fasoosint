#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_falsepos.py — FasoOSINT
Détecte et supprime les faux positifs de sites.json
"""

import asyncio
import aiohttp
import json
from pathlib import Path

SITES_FILE = Path(__file__).parent / "data" / "sites.json"
TEST_USER  = "xzxzxzxzxzxz99999fasoosint"

def load_sites():
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sites(sites):
    with open(SITES_FILE, "w", encoding="utf-8") as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)

async def check(session, site, semaphore):
    url = site["url"].format(username=TEST_USER)
    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10),
                                   allow_redirects=True, ssl=False) as resp:
                text = await resp.text()
                if site.get("error_type") == "status_code":
                    found = resp.status == 200
                elif site.get("error_type") == "message":
                    emsg = site.get("error_msg", "")
                    found = emsg not in text
                else:
                    found = resp.status == 200
                return site, found
        except Exception:
            return site, False

async def main():
    sites = load_sites()
    print(f"[>] {len(sites)} sites chargés")
    print(f"[>] Test avec username impossible : {TEST_USER}")
    print(f"[>] Recherche des faux positifs...\n")

    semaphore = asyncio.Semaphore(50)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    connector = aiohttp.TCPConnector(ssl=False, limit=50)

    false_positives = []
    clean_sites = []

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [check(session, site, semaphore) for site in sites]
        results = await asyncio.gather(*tasks)

    for site, found in results:
        if found:
            print(f"  [❌ FAUX POSITIF] {site['name']}")
            false_positives.append(site)
        else:
            clean_sites.append(site)

    print(f"\n[★] Faux positifs détectés : {len(false_positives)}")
    print(f"[★] Sites valides restants  : {len(clean_sites)}")

    save_sites(clean_sites)
    print(f"[✅] sites.json nettoyé — {len(clean_sites)} sites fiables")

asyncio.run(main())
