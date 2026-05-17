#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
email_osint.py — FasoOSINT
Génère et vérifie les emails possibles liés à un username.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
WHITE  = "\033[97m"
RESET  = "\033[0m"

# Domaines email les plus communs
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "protonmail.com", "icloud.com", "mail.com", "zoho.com",
    "yandex.com", "aol.com", "live.com", "msn.com",
    "yahoo.fr", "hotmail.fr", "laposte.net", "orange.fr",
    "sfr.fr", "free.fr", "wanadoo.fr",
]

GRAVATAR_URL = "https://www.gravatar.com/avatar/{md5}?d=404"
HIBP_URL     = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}"

async def check_gravatar(session, email, semaphore):
    import hashlib
    async with semaphore:
        try:
            md5 = hashlib.md5(email.lower().encode()).hexdigest()
            url = GRAVATAR_URL.format(md5=md5)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8),
                                   ssl=False) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
    return False

async def check_email(session, email, semaphore):
    async with semaphore:
        results = {"email": email, "gravatar": False, "valid": False}
        try:
            # Vérification Gravatar
            import hashlib
            md5 = hashlib.md5(email.lower().encode()).hexdigest()
            url = GRAVATAR_URL.format(md5=md5)
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8),
                                   ssl=False) as resp:
                if resp.status == 200:
                    results["gravatar"] = True
                    results["valid"] = True
        except Exception:
            pass
        return results

async def search_emails(username, domains=None, output_dir="output"):
    if domains is None:
        domains = EMAIL_DOMAINS

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Génère les variantes d'emails
    emails = []
    for domain in domains:
        emails.append(f"{username}@{domain}")
        emails.append(f"{username}1@{domain}")
        emails.append(f"{username}_@{domain}")

    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    print(f"  {RED}★ {GREEN}Recherche emails pour : {WHITE}{username}{RESET}")
    print(f"  {YELLOW}→ {len(emails)} combinaisons à tester{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")

    semaphore = asyncio.Semaphore(20)
    headers = {"User-Agent": "Mozilla/5.0"}
    connector = aiohttp.TCPConnector(ssl=False)

    found_emails = []

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [check_email(session, email, semaphore) for email in emails]
        results = await asyncio.gather(*tasks)

    for r in results:
        if r.get("valid"):
            found_emails.append(r)
            sources = []
            if r.get("gravatar"):
                sources.append("Gravatar")
            print(f"  {GREEN}✅ Email potentiel{RESET}  {YELLOW}{r['email']:<35}{RESET}  {WHITE}[{', '.join(sources)}]{RESET}")

    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    if found_emails:
        print(f"  {RED}★ {GREEN}{len(found_emails)} email(s) potentiel(s) trouvé(s){RESET}")
    else:
        print(f"  {RED}★ {YELLOW}Aucun email vérifié trouvé{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")

    # Sauvegarde
    report = {"username": username, "emails_found": len(found_emails), "emails": found_emails}
    path = output_dir / f"{username}_emails.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  {GREEN}💾 Rapport sauvegardé : {path}{RESET}\n")

    return found_emails

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 email_osint.py <username> [output_dir]")
        sys.exit(1)
    username = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    asyncio.run(search_emails(username, output_dir=output_dir))
