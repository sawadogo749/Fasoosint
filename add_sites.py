#!/usr/bin/env python3
import json
from pathlib import Path

SITES_FILE = Path("data/sites.json")

with open(SITES_FILE, "r", encoding="utf-8") as f:
    sites = json.load(f)

names = {s["name"].lower() for s in sites}

to_add = [
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/{username}/",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
    {
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{username}/",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
    {
        "name": "Snapchat",
        "url": "https://www.snapchat.com/add/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
    {
        "name": "Duolingo",
        "url": "https://www.duolingo.com/profile/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "education",
        "region": "global"
    },
    {
        "name": "TryHackMe",
        "url": "https://tryhackme.com/p/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "security",
        "region": "global"
    },
    {
        "name": "HackTheBox",
        "url": "https://app.hackthebox.com/profile/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "security",
        "region": "global"
    },
    {
        "name": "Telegram",
        "url": "https://t.me/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
    {
        "name": "Discord",
        "url": "https://discord.com/users/{username}",
        "error_type": "status_code",
        "error_msg": "",
        "category": "social",
        "region": "global"
    },
]

added = 0
for site in to_add:
    if site["name"].lower() not in names:
        sites.append(site)
        names.add(site["name"].lower())
        added += 1
        print(f"Ajouté : {site['name']}")
    else:
        print(f"Déjà présent : {site['name']}")

with open(SITES_FILE, "w", encoding="utf-8") as f:
    json.dump(sites, f, ensure_ascii=False, indent=2)

print(f"\nTotal : {len(sites)} sites ({added} ajoutés)")
