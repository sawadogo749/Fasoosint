#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
avatar.py — FasoOSINT
Télécharge automatiquement les photos de profil
depuis GitHub, Gravatar, GitLab, Keybase, Reddit.
"""

import asyncio
import aiohttp
import hashlib
import json
import sys
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
WHITE  = "\033[97m"
RESET  = "\033[0m"

AVATAR_SOURCES = [
    {
        "name": "GitHub",
        "url": "https://github.com/{username}.png",
        "type": "direct"
    },
    {
        "name": "Gravatar",
        "url": "https://www.gravatar.com/avatar/{md5}?d=404&s=200",
        "type": "gravatar"
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{username}.png",
        "type": "direct"
    },
    {
        "name": "Keybase",
        "url": "https://keybase.io/{username}/picture",
        "type": "direct"
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{username}/about.json",
        "type": "reddit"
    },
]

async def download_avatar(session, source, username, output_dir, semaphore):
    async with semaphore:
        try:
            if source["type"] == "gravatar":
                md5 = hashlib.md5(username.lower().encode()).hexdigest()
                url = source["url"].format(md5=md5)
            else:
                url = source["url"].format(username=username)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10),
                                   ssl=False, headers=headers) as resp:

                if resp.status != 200:
                    return None

                content_type = resp.headers.get("content-type", "")

                # Reddit — extraire l'URL avatar depuis JSON
                if source["type"] == "reddit":
                    try:
                        data = await resp.json()
                        icon = data.get("data", {}).get("icon_img", "")
                        if icon and "www.redditstatic.com" not in icon and icon.strip():
                            async with session.get(icon, timeout=aiohttp.ClientTimeout(total=10),
                                                   ssl=False) as img_resp:
                                if img_resp.status == 200:
                                    img_data = await img_resp.read()
                                    if len(img_data) > 1000:
                                        path = output_dir / f"{username}_avatar_reddit.jpg"
                                        with open(path, "wb") as f:
                                            f.write(img_data)
                                        return {"source": source["name"], "path": str(path), "url": icon}
                    except Exception:
                        return None
                    return None

                # Image directe
                img_data = await resp.read()

                # Ignore les images trop petites (avatars par défaut)
                if len(img_data) < 2000:
                    return None

                ext = "jpg"
                if "png" in content_type:
                    ext = "png"
                elif "gif" in content_type:
                    ext = "gif"

                path = output_dir / f"{username}_avatar_{source['name'].lower()}.{ext}"
                with open(path, "wb") as f:
                    f.write(img_data)
                return {"source": source["name"], "path": str(path), "url": url}

        except Exception:
            return None

async def fetch_all_avatars(username, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    avatar_dir = output_dir / f"{username}_avatars"
    avatar_dir.mkdir(exist_ok=True)

    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    print(f"  {RED}★ {GREEN}Recherche photos de profil : {WHITE}{username}{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")

    semaphore = asyncio.Semaphore(10)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    connector = aiohttp.TCPConnector(ssl=False)

    found_avatars = []

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [download_avatar(session, source, username, avatar_dir, semaphore)
                 for source in AVATAR_SOURCES]
        results = await asyncio.gather(*tasks)

    for r in results:
        if r:
            found_avatars.append(r)
            print(f"  {GREEN}✅ Avatar trouvé{RESET}  {YELLOW}{r['source']:<15}{RESET}  {WHITE}{r['path']}{RESET}")

    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    if found_avatars:
        print(f"  {RED}★ {GREEN}{len(found_avatars)} photo(s) téléchargée(s) → {WHITE}{avatar_dir}{RESET}")
    else:
        print(f"  {RED}★ {YELLOW}Aucune photo de profil publique trouvée{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")

    report = {
        "username": username,
        "avatars_found": len(found_avatars),
        "avatars": found_avatars
    }
    report_path = output_dir / f"{username}_avatars.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return found_avatars

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 avatar.py <username> [output_dir]")
        sys.exit(1)
    username = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    asyncio.run(fetch_all_avatars(username, output_dir))
