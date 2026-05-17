#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import os
import sys
import csv
import argparse
import time
import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

VERSION = "1.0.0"

RED    = Fore.RED
GREEN  = Fore.GREEN
YELLOW = Fore.YELLOW
WHITE  = Fore.WHITE
RESET  = Style.RESET_ALL

BANNER = f"""
{RED}  ███████╗{GREEN}█████╗ {YELLOW}███████╗{RED}██████╗ {GREEN} ██████╗{YELLOW}███████╗{RED}██╗{GREEN}███╗   ██╗{YELLOW}████████╗{RESET}
{RED}  ██╔════╝{GREEN}██╔══██╗{YELLOW}██╔════╝{RED}██╔═══██╗{GREEN}██╔═══██╗{YELLOW}██╔════╝{RED}██║{GREEN}████╗  ██║{YELLOW}╚══██╔══╝{RESET}
{RED}  █████╗  {GREEN}███████║{YELLOW}███████╗{RED}██║   ██║{GREEN}██║   ██║{YELLOW}███████╗{RED}██║{GREEN}██╔██╗ ██║{YELLOW}   ██║{RESET}
{RED}  ██╔══╝  {GREEN}██╔══██║{YELLOW}╚════██║{RED}██║   ██║{GREEN}██║   ██║{YELLOW}╚════██║{RED}██║{GREEN}██║╚██╗██║{YELLOW}   ██║{RESET}
{RED}  ██║     {GREEN}██║  ██║{YELLOW}███████║{RED}╚██████╔╝{GREEN}╚██████╔╝{YELLOW}███████║{RED}██║{GREEN}██║ ╚████║{YELLOW}   ██║{RESET}
{RED}  ╚═╝     {GREEN}╚═╝  ╚═╝{YELLOW}╚══════╝{RED} ╚═════╝{GREEN} ╚═════╝{YELLOW} ╚══════╝{RED}╚═╝{GREEN}╚═╝  ╚═══╝{YELLOW}   ╚═╝{RESET}

{RED}  ★{YELLOW} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ {RED}★{RESET}
{RED}  ★ {GREEN}v{VERSION}  {YELLOW}|  OSINT Username Intelligence Tool  {RED}|  {YELLOW}🔍  {RED}★{RESET}
{RED}  ★{YELLOW} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ {RED}★{RESET}
"""

MESSAGES = {
    "fr": {
        "searching": "🔍 Recherche de",
        "found": "✅ TROUVÉ",
        "not_found": "❌ Non trouvé",
        "error": "⚠️  Erreur",
        "done": "✔  Terminé en",
        "results": "profils trouvés sur",
        "sites": "sites",
        "saving_txt": "💾 Résultats sauvegardés",
        "saving_csv": "📊 CSV exporté",
        "saving_html": "🌐 Rapport HTML généré",
        "language_set": "🌍 Langue : Français",
        "timeout": "délai dépassé",
        "total": "TOTAL",
        "report_title": "Rapport FasoOSINT",
    },
    "en": {
        "searching": "🔍 Searching for",
        "found": "✅ FOUND",
        "not_found": "❌ Not found",
        "error": "⚠️  Error",
        "done": "✔  Completed in",
        "results": "profiles found across",
        "sites": "sites",
        "saving_txt": "💾 Results saved",
        "saving_csv": "📊 CSV exported",
        "saving_html": "🌐 HTML report generated",
        "language_set": "🌍 Language: English",
        "timeout": "timeout",
        "total": "TOTAL",
        "report_title": "FasoOSINT Report",
    }
}

DATA_FILE = Path(__file__).parent / "data" / "sites.json"

def load_sites():
    if not DATA_FILE.exists():
        print(f"{RED}[!] sites.json introuvable : {DATA_FILE}{RESET}")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def check_site(session, site, username, lang, results, semaphore, timeout=10):
    msg = MESSAGES[lang]
    url = site["url"].format(username=username)
    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout),
                                   allow_redirects=True, ssl=False) as resp:
                text = await resp.text()
                found = False
                if site.get("error_type") == "status_code":
                    found = resp.status == 200
                elif site.get("error_type") == "message":
                    error_msg = site.get("error_msg", "")
                    found = error_msg not in text
                else:
                    found = resp.status == 200

                if found:
                    print(f"  {GREEN}{msg['found']}{RESET}  {YELLOW}{site['name']:<28}{RESET}  {WHITE}{url}{RESET}")
                    results.append({"site": site["name"], "url": url, "status": "found",
                                    "http_code": resp.status, "category": site.get("category", "")})
                else:
                    if "--verbose" in sys.argv or "-v" in sys.argv:
                        print(f"  {RED}{msg['not_found']}{RESET}  {site['name']}")
                    results.append({"site": site["name"], "url": url, "status": "not_found",
                                    "http_code": resp.status, "category": site.get("category", "")})
        except asyncio.TimeoutError:
            if "--verbose" in sys.argv or "-v" in sys.argv:
                print(f"  {YELLOW}{msg['error']}{RESET}  {site['name']} ({msg['timeout']})")
            results.append({"site": site["name"], "url": url, "status": "timeout",
                            "http_code": 0, "category": site.get("category", "")})
        except Exception:
            results.append({"site": site["name"], "url": url, "status": "error",
                            "http_code": 0, "category": site.get("category", "")})

async def run_search(username, lang, concurrency=50, filter_region=None,
                     filter_category=None, timeout=10):
    msg = MESSAGES[lang]
    sites = load_sites()

    if filter_region:
        sites = [s for s in sites if s.get("region", "").lower() == filter_region.lower()]
    if filter_category:
        sites = [s for s in sites if s.get("category", "").lower() == filter_category.lower()]

    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    print(f"  {RED}★ {GREEN}{msg['searching']} {WHITE}{username}{GREEN} sur {len(sites)} sites {RED}★{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")

    results = []
    semaphore = asyncio.Semaphore(concurrency)
    start = time.time()

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    connector = aiohttp.TCPConnector(ssl=False, limit=concurrency)

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [check_site(session, site, username, lang, results, semaphore, timeout)
                 for site in sites]
        await asyncio.gather(*tasks)

    elapsed = round(time.time() - start, 2)
    found = [r for r in results if r["status"] == "found"]

    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    print(f"  {RED}★ {GREEN}{msg['total']} : {YELLOW}{len(found)} {GREEN}{msg['results']} {YELLOW}{len(sites)} {GREEN}{msg['sites']} — {YELLOW}{elapsed}s {RED}★{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")

    return results, found, elapsed

def save_txt(username, found, lang, output_dir):
    msg = MESSAGES[lang]
    path = output_dir / f"{username}_fasoosint.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"FasoOSINT — {msg['report_title']}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Profiles found: {len(found)}\n")
        f.write("=" * 60 + "\n\n")
        for r in found:
            f.write(f"[{r['category']}] {r['site']}: {r['url']}\n")
    print(f"  {GREEN}{msg['saving_txt']}: {path}{RESET}")

def save_csv(username, results, lang, output_dir):
    msg = MESSAGES[lang]
    path = output_dir / f"{username}_fasoosint.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "url", "status", "http_code", "category"])
        writer.writeheader()
        writer.writerows(results)
    print(f"  {GREEN}{msg['saving_csv']}: {path}{RESET}")

def save_html(username, found, all_results, lang, output_dir, elapsed):
    msg = MESSAGES[lang]
    path = output_dir / f"{username}_fasoosint.html"

    categories = {}
    for r in found:
        cat = r.get("category") or "Other"
        categories.setdefault(cat, []).append(r)

    cat_rows = ""
    for cat, items in categories.items():
        cat_rows += f"<tr><td colspan='3' class='cat-header'>★ {cat.upper()} ({len(items)})</td></tr>"
        for item in items:
            cat_rows += f"""<tr>
              <td>{item['site']}</td>
              <td><a href='{item['url']}' target='_blank'>{item['url']}</a></td>
              <td class='found'>✅</td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FasoOSINT — {username}</title>
<style>
  :root {{
    --red:    #EF2B2D;
    --green:  #009A00;
    --yellow: #FFD700;
    --dark:   #0a0a0a;
    --card:   #111;
    --border: #1e1e1e;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--dark); color: #ccc; font-family: 'Courier New', monospace; padding: 2rem; }}
  .flag-bar {{ height: 6px; background: linear-gradient(90deg, var(--red) 50%, var(--green) 50%); border-radius: 3px; margin-bottom: 2rem; position: relative; }}
  .flag-bar::after {{ content: '★'; position: absolute; left: 50%; transform: translateX(-50%) translateY(-40%); color: var(--yellow); font-size: 1.2rem; }}
  h1 {{ color: var(--red); font-size: 2rem; margin-bottom: .3rem; }}
  h1 span {{ color: var(--green); }}
  h1 em {{ color: var(--yellow); font-style: normal; }}
  .meta {{ color: #555; margin-bottom: 2rem; font-size: .85rem; }}
  .stats {{ display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }}
  .stat {{ background: var(--card); border: 1px solid var(--border); border-left: 4px solid var(--red); padding: 1rem 1.5rem; border-radius: 4px; }}
  .stat.green {{ border-left-color: var(--green); }}
  .stat.yellow {{ border-left-color: var(--yellow); }}
  .stat-val {{ font-size: 2rem; color: var(--red); font-weight: bold; }}
  .stat.green .stat-val {{ color: var(--green); }}
  .stat.yellow .stat-val {{ color: var(--yellow); }}
  .stat-label {{ font-size: .8rem; color: #666; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; }}
  th {{ background: #1a1a1a; padding: .75rem 1rem; text-align: left; font-size: .85rem; }}
  th:nth-child(1) {{ color: var(--red); }}
  th:nth-child(2) {{ color: var(--green); }}
  th:nth-child(3) {{ color: var(--yellow); }}
  td {{ padding: .6rem 1rem; border-bottom: 1px solid var(--border); font-size: .85rem; }}
  td a {{ color: var(--green); text-decoration: none; }}
  td a:hover {{ color: var(--yellow); }}
  .cat-header {{ background: #161616; font-size: .75rem; text-transform: uppercase; letter-spacing: 2px; color: var(--yellow); }}
  .found {{ color: var(--green); }}
  .footer {{ margin-top: 2rem; color: #333; font-size: .75rem; text-align: center; }}
  .footer span {{ color: var(--yellow); }}
  .flag-bar-bottom {{ height: 6px; background: linear-gradient(90deg, var(--red) 50%, var(--green) 50%); border-radius: 3px; margin-top: 2rem; }}
</style>
</head>
<body>
<div class="flag-bar"></div>
<h1>🔍 <span>Faso</span><em>OSINT</em></h1>
<div class="meta">{msg['report_title']} — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
<div class="stats">
  <div class="stat"><div class="stat-val">{username}</div><div class="stat-label">Username</div></div>
  <div class="stat green"><div class="stat-val">{len(found)}</div><div class="stat-label">{msg['results']} {len(all_results)} {msg['sites']}</div></div>
  <div class="stat yellow"><div class="stat-val">{elapsed}s</div><div class="stat-label">Duration</div></div>
  <div class="stat"><div class="stat-val">{len(categories)}</div><div class="stat-label">Categories</div></div>
</div>
<table>
  <thead><tr><th>Site</th><th>URL</th><th>Status</th></tr></thead>
  <tbody>{cat_rows}</tbody>
</table>
<div class="flag-bar-bottom"></div>
<div class="footer">FasoOSINT v{VERSION} — <span>github.com/yourusername/fasoosint</span></div>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  {GREEN}{msg['saving_html']}: {path}{RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="FasoOSINT — OSINT Username Intelligence Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python fasoosint.py johndoe
  python fasoosint.py johndoe --lang en --html
  python fasoosint.py johndoe --region africa --all
  python fasoosint.py johndoe --category social --csv
        """
    )
    parser.add_argument("username", help="Pseudonyme à rechercher")
    parser.add_argument("--lang", choices=["fr", "en"], default="fr")
    parser.add_argument("--txt", action="store_true")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--region", help="africa | global")
    parser.add_argument("--category", help="social | gaming | coding | africa ...")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--output", default="output")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=f"FasoOSINT v{VERSION}")

    args = parser.parse_args()
    lang = args.lang

    print(BANNER)
    print(f"  {YELLOW}{MESSAGES[lang]['language_set']}{RESET}\n")

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    results, found, elapsed = asyncio.run(
        run_search(args.username, lang,
                   concurrency=args.concurrency,
                   filter_region=args.region,
                   filter_category=args.category,
                   timeout=args.timeout)
    )

    if args.all or args.txt:
        save_txt(args.username, found, lang, output_dir)
    if args.all or args.csv:
        save_csv(args.username, results, lang, output_dir)
    if args.all or args.html:
        save_html(args.username, found, results, lang, output_dir, elapsed)
    if not (args.all or args.txt or args.csv or args.html):
        save_txt(args.username, found, lang, output_dir)

if __name__ == "__main__":
    main()
