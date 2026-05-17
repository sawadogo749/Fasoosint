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
        "saving_pdf": "📄 Rapport PDF généré",
        "language_set": "🌍 Langue : Français",
        "timeout": "délai dépassé",
        "total": "TOTAL",
        "report_title": "Rapport FasoOSINT",
        "score_label": "Score OSINT",
        "variants_testing": "Test des variantes",
        "variants_summary": "RÉSUMÉ VARIANTS",
        "variants_found": "profils trouvés",
        "avatar_search": "Recherche photos de profil",
        "email_search": "Recherche emails",
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
        "saving_pdf": "📄 PDF report generated",
        "language_set": "🌍 Language: English",
        "timeout": "timeout",
        "total": "TOTAL",
        "report_title": "FasoOSINT Report",
        "score_label": "OSINT Score",
        "variants_testing": "Testing variants",
        "variants_summary": "VARIANTS SUMMARY",
        "variants_found": "profiles found",
        "avatar_search": "Searching profile pictures",
        "email_search": "Searching emails",
    }
}

DATA_FILE = Path(__file__).parent / "data" / "sites.json"

def load_sites():
    if not DATA_FILE.exists():
        print(f"{RED}[!] sites.json introuvable : {DATA_FILE}{RESET}")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_variants(username):
    parts = username.strip().lower().split()
    if len(parts) >= 2:
        first, last = parts[0], parts[-1]
        variants = [
            first + last,
            first + "_" + last,
            first + "." + last,
            first[0] + last,
            last + first,
            last + "_" + first,
            first[0] + "." + last,
            first,
            last,
            first + last + "1",
            first + last + "123",
        ]
    else:
        base = parts[0]
        variants = [
            base,
            base + "1",
            base + "2",
            base + "123",
        ]
    seen = []
    for v in variants:
        if v not in seen:
            seen.append(v)
    return seen

def compute_score(found, total_sites):
    if not found:
        return 0, "Aucune exposition", "No exposure"
    ratio = len(found) / total_sites
    score_count = min(int(ratio * 200), 40)
    cats = set(r.get("category", "") for r in found)
    score_cats = min(len(cats) * 3, 20)
    sensitive = {"security", "crypto", "dating", "adult"}
    sensitive_count = sum(1 for r in found if r.get("category") in sensitive)
    score_sensitive = min(sensitive_count * 4, 20)
    regions = set(r.get("region", "global") for r in found)
    score_region = min(len(regions) * 10, 20)
    total = score_count + score_cats + score_sensitive + score_region
    if total <= 20:
        label_fr, label_en = "Faible exposition", "Low exposure"
    elif total <= 40:
        label_fr, label_en = "Exposition modérée", "Moderate exposure"
    elif total <= 60:
        label_fr, label_en = "Exposition significative", "Significant exposure"
    elif total <= 80:
        label_fr, label_en = "Exposition élevée", "High exposure"
    else:
        label_fr, label_en = "EXPOSITION CRITIQUE", "CRITICAL EXPOSURE"
    return total, label_fr, label_en

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
                    results.append({
                        "site": site["name"], "url": url, "status": "found",
                        "http_code": resp.status, "category": site.get("category", ""),
                        "region": site.get("region", "global")
                    })
                else:
                    if "--verbose" in sys.argv or "-v" in sys.argv:
                        print(f"  {RED}{msg['not_found']}{RESET}  {site['name']}")
                    results.append({
                        "site": site["name"], "url": url, "status": "not_found",
                        "http_code": resp.status, "category": site.get("category", ""),
                        "region": site.get("region", "global")
                    })
        except asyncio.TimeoutError:
            if "--verbose" in sys.argv or "-v" in sys.argv:
                print(f"  {YELLOW}{msg['error']}{RESET}  {site['name']} ({msg['timeout']})")
            results.append({
                "site": site["name"], "url": url, "status": "timeout",
                "http_code": 0, "category": site.get("category", ""),
                "region": site.get("region", "global")
            })
        except Exception:
            results.append({
                "site": site["name"], "url": url, "status": "error",
                "http_code": 0, "category": site.get("category", ""),
                "region": site.get("region", "global")
            })

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
    score, label_fr, label_en = compute_score(found, len(sites))
    label = label_fr if lang == "fr" else label_en
    if score <= 20:
        sc = GREEN
    elif score <= 50:
        sc = YELLOW
    else:
        sc = RED
    filled = int(score / 5)
    bar = f"{sc}{'█' * filled}{RESET}{'░' * (20 - filled)}"
    print(f"\n  {YELLOW}{'━'*62}{RESET}")
    print(f"  {RED}★ {GREEN}{msg['total']} : {YELLOW}{len(found)} {GREEN}{msg['results']} {YELLOW}{len(sites)} {GREEN}{msg['sites']} — {YELLOW}{elapsed}s {RED}★{RESET}")
    print(f"  {RED}★ {GREEN}{msg['score_label']} : {sc}{score}/100{RESET} [{bar}] {sc}{label}{RESET} {RED}★{RESET}")
    print(f"  {YELLOW}{'━'*62}{RESET}\n")
    return results, found, elapsed, score, label

def save_txt(username, found, lang, output_dir, score, label):
    msg = MESSAGES[lang]
    path = output_dir / f"{username}_fasoosint.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"FasoOSINT — {msg['report_title']}\n")
        f.write(f"Username  : {username}\n")
        f.write(f"Date      : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Profiles  : {len(found)}\n")
        f.write(f"Score     : {score}/100 — {label}\n")
        f.write("=" * 60 + "\n\n")
        cats = {}
        for r in found:
            cat = r.get("category") or "other"
            cats.setdefault(cat, []).append(r)
        for cat, items in cats.items():
            f.write(f"\n[{cat.upper()}]\n")
            for r in items:
                f.write(f"  {r['site']}: {r['url']}\n")
    print(f"  {GREEN}{msg['saving_txt']}: {path}{RESET}")

def save_csv(username, results, lang, output_dir):
    msg = MESSAGES[lang]
    path = output_dir / f"{username}_fasoosint.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["site", "url", "status", "http_code", "category", "region"])
        writer.writeheader()
        writer.writerows(results)
    print(f"  {GREEN}{msg['saving_csv']}: {path}{RESET}")

def save_html(username, found, all_results, lang, output_dir, elapsed, score, label):
    msg = MESSAGES[lang]
    path = output_dir / f"{username}_fasoosint.html"
    categories = {}
    for r in found:
        cat = r.get("category") or "Other"
        categories.setdefault(cat, []).append(r)
    if score <= 20:
        score_color = "#009A00"
    elif score <= 50:
        score_color = "#FFD700"
    else:
        score_color = "#EF2B2D"
    cat_rows = ""
    for cat, items in categories.items():
        cat_rows += f"<tr><td colspan='3' class='cat-header'>★ {cat.upper()} ({len(items)})</td></tr>"
        for item in items:
            cat_rows += f"<tr><td>{item['site']}</td><td><a href='{item['url']}' target='_blank'>{item['url']}</a></td><td class='found'>✅</td></tr>"
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FasoOSINT — {username}</title>
<style>
  :root {{ --red: #EF2B2D; --green: #009A00; --yellow: #FFD700; --dark: #0a0a0a; --card: #111; --border: #1e1e1e; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--dark); color: #ccc; font-family: 'Courier New', monospace; padding: 2rem; }}
  .flag-bar {{ height: 6px; background: linear-gradient(90deg, var(--red) 50%, var(--green) 50%); border-radius: 3px; margin-bottom: 2rem; position: relative; }}
  .flag-bar::after {{ content: '★'; position: absolute; left: 50%; transform: translateX(-50%) translateY(-40%); color: var(--yellow); font-size: 1.2rem; }}
  h1 {{ font-size: 2rem; margin-bottom: .3rem; }}
  h1 .r {{ color: var(--red); }} h1 .g {{ color: var(--green); }} h1 .y {{ color: var(--yellow); }}
  .meta {{ color: #555; margin-bottom: 2rem; font-size: .85rem; }}
  .stats {{ display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap; }}
  .stat {{ background: var(--card); border: 1px solid var(--border); border-left: 4px solid var(--red); padding: 1rem 1.5rem; border-radius: 4px; }}
  .stat.green {{ border-left-color: var(--green); }} .stat.yellow {{ border-left-color: var(--yellow); }}
  .stat-val {{ font-size: 2rem; color: var(--red); font-weight: bold; }}
  .stat.green .stat-val {{ color: var(--green); }} .stat.yellow .stat-val {{ color: var(--yellow); }}
  .stat-label {{ font-size: .8rem; color: #666; }}
  .score-box {{ background: var(--card); border: 1px solid var(--border); border-left: 4px solid {score_color}; border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; }}
  .score-title {{ font-size: .8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: .5rem; }}
  .score-val {{ font-size: 3rem; font-weight: bold; color: {score_color}; }}
  .score-label {{ font-size: 1rem; color: {score_color}; margin-top: .3rem; }}
  .score-bar-wrap {{ background: #1a1a1a; border-radius: 4px; height: 8px; margin-top: 1rem; overflow: hidden; }}
  .score-bar {{ height: 8px; width: {score}%; background: {score_color}; border-radius: 4px; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 8px; overflow: hidden; margin-bottom: 2rem; }}
  th {{ background: #1a1a1a; padding: .75rem 1rem; text-align: left; font-size: .85rem; }}
  th:nth-child(1) {{ color: var(--red); }} th:nth-child(2) {{ color: var(--green); }} th:nth-child(3) {{ color: var(--yellow); }}
  td {{ padding: .6rem 1rem; border-bottom: 1px solid var(--border); font-size: .85rem; }}
  td a {{ color: var(--green); text-decoration: none; }} td a:hover {{ color: var(--yellow); }}
  .cat-header {{ background: #161616; font-size: .75rem; text-transform: uppercase; letter-spacing: 2px; color: var(--yellow); }}
  .found {{ color: var(--green); }}
  .footer {{ color: #333; font-size: .75rem; text-align: center; margin-top: 1rem; }}
  .footer span {{ color: var(--yellow); }}
  .flag-bar-bottom {{ height: 6px; background: linear-gradient(90deg, var(--red) 50%, var(--green) 50%); border-radius: 3px; margin-top: 2rem; }}
</style>
</head>
<body>
<div class="flag-bar"></div>
<h1>🔍 <span class="r">Faso</span><span class="g">OSINT</span> <span class="y">★</span></h1>
<div class="meta">{msg['report_title']} — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
<div class="stats">
  <div class="stat"><div class="stat-val">{username}</div><div class="stat-label">Username</div></div>
  <div class="stat green"><div class="stat-val">{len(found)}</div><div class="stat-label">{msg['results']} {len(all_results)} {msg['sites']}</div></div>
  <div class="stat yellow"><div class="stat-val">{elapsed}s</div><div class="stat-label">Duration</div></div>
  <div class="stat"><div class="stat-val">{len(categories)}</div><div class="stat-label">Categories</div></div>
</div>
<div class="score-box">
  <div class="score-title">{msg['score_label']}</div>
  <div class="score-val">{score}<span style="font-size:1.5rem;color:#444">/100</span></div>
  <div class="score-label">{label}</div>
  <div class="score-bar-wrap"><div class="score-bar"></div></div>
</div>
<table>
  <thead><tr><th>Site</th><th>URL</th><th>Status</th></tr></thead>
  <tbody>{cat_rows}</tbody>
</table>
<div class="flag-bar-bottom"></div>
<div class="footer">FasoOSINT v{VERSION} — <span>github.com/sawadogo749/Fasoosint</span></div>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  {GREEN}{msg['saving_html']}: {path}{RESET}")

def save_pdf(username, found, lang, output_dir, elapsed, score, label):
    msg = MESSAGES[lang]
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
        from reportlab.lib.units import cm
        path = output_dir / f"{username}_fasoosint.pdf"
        RED_PDF    = colors.HexColor("#EF2B2D")
        GREEN_PDF  = colors.HexColor("#009A00")
        YELLOW_PDF = colors.HexColor("#FFD700")
        DARK_PDF   = colors.HexColor("#0a0a0a")
        CARD_PDF   = colors.HexColor("#111111")
        doc = SimpleDocTemplate(str(path), pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        story = []
        title_style = ParagraphStyle("title", fontSize=24, textColor=RED_PDF,
                                     fontName="Helvetica-Bold", spaceAfter=6)
        story.append(Paragraph("FasoOSINT ★", title_style))
        sub_style = ParagraphStyle("sub", fontSize=10, textColor=colors.grey, spaceAfter=20)
        story.append(Paragraph(f"{msg['report_title']} — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", sub_style))
        story.append(HRFlowable(width="100%", color=RED_PDF, thickness=2))
        story.append(Spacer(1, 0.5*cm))
        stat_data = [["Username", "Profils", "Sites", "Durée"],
                     [username, str(len(found)), str(len(found)), f"{elapsed}s"]]
        stat_table = Table(stat_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        stat_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), DARK_PDF),
            ("TEXTCOLOR",     (0,0), (-1,0), GREEN_PDF),
            ("TEXTCOLOR",     (0,1), (-1,-1), colors.white),
            ("BACKGROUND",    (0,1), (-1,1), CARD_PDF),
            ("FONTNAME",      (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#1e1e1e")),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(stat_table)
        story.append(Spacer(1, 0.5*cm))
        score_color_pdf = GREEN_PDF if score <= 20 else (YELLOW_PDF if score <= 50 else RED_PDF)
        score_style = ParagraphStyle("score", fontSize=16, textColor=score_color_pdf,
                                     fontName="Helvetica-Bold", spaceAfter=4)
        story.append(Paragraph(f"Score OSINT : {score}/100 — {label}", score_style))
        story.append(HRFlowable(width=f"{score}%", color=score_color_pdf, thickness=6))
        story.append(Spacer(1, 0.5*cm))
        categories = {}
        for r in found:
            cat = r.get("category") or "other"
            categories.setdefault(cat, []).append(r)
        for cat, items in categories.items():
            cat_style = ParagraphStyle("cat", fontSize=11, textColor=YELLOW_PDF,
                                       fontName="Helvetica-Bold", spaceAfter=4)
            story.append(Paragraph(f"★ {cat.upper()} ({len(items)})", cat_style))
            table_data = [["Site", "URL"]]
            for item in items:
                url = item['url']
                if len(url) > 60:
                    url = url[:57] + "..."
                table_data.append([item['site'], url])
            t = Table(table_data, colWidths=[5*cm, 11*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), DARK_PDF),
                ("TEXTCOLOR",     (0,0), (-1,0), GREEN_PDF),
                ("TEXTCOLOR",     (0,1), (-1,-1), colors.white),
                ("FONTNAME",      (0,0), (-1,-1), "Helvetica"),
                ("FONTSIZE",      (0,0), (-1,-1), 8),
                ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#1e1e1e")),
                ("ROWBACKGROUNDS",(0,1), (-1,-1), [CARD_PDF, colors.HexColor("#161616")]),
                ("TOPPADDING",    (0,0), (-1,-1), 5),
                ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", color=GREEN_PDF, thickness=1))
        footer_style = ParagraphStyle("footer", fontSize=8, textColor=colors.grey,
                                      alignment=1, spaceBefore=10)
        story.append(Paragraph(f"FasoOSINT v{VERSION} — github.com/sawadogo749/Fasoosint — For educational use only", footer_style))
        doc.build(story)
        print(f"  {GREEN}{msg['saving_pdf']}: {path}{RESET}")
    except ImportError:
        print(f"  {YELLOW}[!] reportlab non installé. Lance : pip install reportlab{RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="FasoOSINT — OSINT Username Intelligence Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python3 fasoosint.py johndoe
  python3 fasoosint.py johndoe --lang en --html
  python3 fasoosint.py johndoe --all
  python3 fasoosint.py "john doe" --variants --lang fr
  python3 fasoosint.py johndoe --avatar
  python3 fasoosint.py johndoe --email
  python3 fasoosint.py johndoe --all --avatar --email
        """
    )
    parser.add_argument("username", help="Pseudonyme à rechercher")
    parser.add_argument("--lang", choices=["fr", "en"], default="fr")
    parser.add_argument("--txt", action="store_true")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--variants", action="store_true")
    parser.add_argument("--avatar", action="store_true", help="Télécharger les photos de profil")
    parser.add_argument("--email", action="store_true", help="Rechercher les emails associés")
    parser.add_argument("--region", help="africa | global")
    parser.add_argument("--category", help="social | gaming | coding | africa ...")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--output", default="output")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=f"FasoOSINT v{VERSION}")

    args = parser.parse_args()
    lang = args.lang
    msg = MESSAGES[lang]

    print(BANNER)
    print(f"  {YELLOW}{msg['language_set']}{RESET}\n")

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # MODE VARIANTS
    if args.variants:
        variants = generate_variants(args.username)
        print(f"  {YELLOW}{'━'*62}{RESET}")
        print(f"  {RED}★ {GREEN}{msg['variants_testing']} : {WHITE}{', '.join(variants)}{RESET}")
        print(f"  {YELLOW}{'━'*62}{RESET}\n")
        all_found = {}
        for variant in variants:
            print(f"\n  {RED}★ {GREEN}→ {WHITE}{variant}{RESET}")
            results, found, elapsed, score, label = asyncio.run(
                run_search(variant, lang,
                           concurrency=args.concurrency,
                           filter_region=args.region,
                           filter_category=args.category,
                           timeout=args.timeout)
            )
            if found:
                all_found[variant] = {"found": found, "score": score, "label": label}
                save_txt(variant, found, lang, output_dir, score, label)
                if args.all or args.html:
                    save_html(variant, found, results, lang, output_dir, elapsed, score, label)
                if args.all or args.csv:
                    save_csv(variant, results, lang, output_dir)
                if args.all or args.pdf:
                    save_pdf(variant, found, lang, output_dir, elapsed, score, label)
        print(f"\n  {YELLOW}{'━'*62}{RESET}")
        print(f"  {RED}★ {GREEN}{msg['variants_summary']} :{RESET}")
        for v, data in all_found.items():
            sc = GREEN if data['score'] <= 20 else (YELLOW if data['score'] <= 50 else RED)
            print(f"  {YELLOW}→ {WHITE}{v:<20}{YELLOW} : {sc}{len(data['found'])} {msg['variants_found']} — Score {data['score']}/100{RESET}")
        if not all_found:
            print(f"  {RED}→ Aucun profil trouvé{RESET}")
        print(f"  {YELLOW}{'━'*62}{RESET}\n")
        sys.exit(0)

    # MODE NORMAL
    results, found, elapsed, score, label = asyncio.run(
        run_search(args.username, lang,
                   concurrency=args.concurrency,
                   filter_region=args.region,
                   filter_category=args.category,
                   timeout=args.timeout)
    )

    if args.all or args.txt:
        save_txt(args.username, found, lang, output_dir, score, label)
    if args.all or args.csv:
        save_csv(args.username, results, lang, output_dir)
    if args.all or args.html:
        save_html(args.username, found, results, lang, output_dir, elapsed, score, label)
    if args.all or args.pdf:
        save_pdf(args.username, found, lang, output_dir, elapsed, score, label)
    if not (args.all or args.txt or args.csv or args.html or args.pdf):
        save_txt(args.username, found, lang, output_dir, score, label)

    # MODULE AVATAR
    if args.avatar or args.all:
        print(f"\n  {YELLOW}{'━'*62}{RESET}")
        print(f"  {RED}★ {GREEN}{msg['avatar_search']} : {WHITE}{args.username}{RESET}")
        print(f"  {YELLOW}{'━'*62}{RESET}\n")
        from avatar import fetch_all_avatars
        asyncio.run(fetch_all_avatars(args.username, output_dir))

    # MODULE EMAIL
    if args.email or args.all:
        print(f"\n  {YELLOW}{'━'*62}{RESET}")
        print(f"  {RED}★ {GREEN}{msg['email_search']} : {WHITE}{args.username}{RESET}")
        print(f"  {YELLOW}{'━'*62}{RESET}\n")
        from email_osint import search_emails
        asyncio.run(search_emails(args.username, output_dir=str(output_dir)))

if __name__ == "__main__":
    main()
