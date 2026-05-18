#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import json
import re
import time
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

sys.path.insert(0, str(Path(__file__).parent.parent))
from fasoosint import run_search, save_html, save_csv, save_txt, VERSION
from avatar import fetch_all_avatars
from email_osint import search_emails

app = Flask(__name__)
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── SÉCURITÉ ──────────────────────────────────────────────
# Username valide : lettres, chiffres, tirets, underscores, points
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9._\-]{1,50}$')

# Mots-clés dangereux à bloquer
BLACKLIST = [
    "select", "insert", "update", "delete", "drop", "union",
    "exec", "execute", "script", "alert", "onerror", "onclick",
    "javascript", "eval", "<", ">", ";", "--", "/*", "*/",
    "xp_", "cmd", "shell", "passwd", "etc/passwd", "proc/self"
]

def is_safe_username(username):
    """Vérifie que le username est sûr."""
    if not username:
        return False
    if not USERNAME_REGEX.match(username):
        return False
    username_lower = username.lower()
    for word in BLACKLIST:
        if word in username_lower:
            return False
    return True

def sanitize_input(text):
    """Nettoie les entrées utilisateur."""
    if not text:
        return ""
    # Supprime les caractères dangereux
    text = re.sub(r'[<>;"\'\\]', '', str(text))
    return text.strip()[:100]

# Rate limiting simple en mémoire
request_counts = {}
RATE_LIMIT = 10  # requêtes par minute par IP

def check_rate_limit(ip):
    now = time.time()
    if ip not in request_counts:
        request_counts[ip] = []
    # Nettoie les anciennes requêtes
    request_counts[ip] = [t for t in request_counts[ip] if now - t < 60]
    if len(request_counts[ip]) >= RATE_LIMIT:
        return False
    request_counts[ip].append(now)
    return True

@app.route("/")
def index():
    return render_template("index.html", version=VERSION)

@app.route("/api/search", methods=["POST"])
def api_search():
    # Rate limiting
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    if not check_rate_limit(ip):
        return jsonify({"error": "Trop de requêtes. Attendez 1 minute."}), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Requête invalide"}), 400

    username = str(data.get("username", "")).strip()
    lang = data.get("lang", "fr")
    region = data.get("region") or None
    category = data.get("category") or None
    export_html = bool(data.get("export_html", False))
    export_csv = bool(data.get("export_csv", False))
    do_avatar = bool(data.get("avatar", False))
    do_email = bool(data.get("email", False))

    # Validation username
    if not is_safe_username(username):
        return jsonify({"error": "Username invalide ou dangereux"}), 400

    # Validation lang
    if lang not in ["fr", "en"]:
        lang = "fr"

    # Validation region et category
    allowed_regions = ["", "global", "africa"]
    allowed_categories = ["", "social", "coding", "gaming", "video", "music",
                          "art", "blog", "forum", "professional", "security",
                          "crypto", "shopping", "sport", "education", "africa", "misc"]
    if region not in allowed_regions:
        region = None
    if category not in allowed_categories:
        category = None

    timeout = 10
    concurrency = 50

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results, found, elapsed, score, label = loop.run_until_complete(
            run_search(username, lang, concurrency=concurrency,
                       filter_region=region, filter_category=category,
                       timeout=timeout)
        )
    finally:
        loop.close()

    exports = []
    if export_html:
        save_html(username, found, results, lang, OUTPUT_DIR, elapsed, score, label)
        exports.append(f"/output/{username}_fasoosint.html")
    if export_csv:
        save_csv(username, results, lang, OUTPUT_DIR)
        exports.append(f"/output/{username}_fasoosint.csv")
    save_txt(username, found, lang, OUTPUT_DIR, score, label)
    exports.append(f"/output/{username}_fasoosint.txt")

    categories = {}
    for r in found:
        cat = r.get("category") or "other"
        categories.setdefault(cat, []).append(r)

    # AVATARS
    avatars = []
    if do_avatar:
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)
        try:
            avatar_results = loop2.run_until_complete(
                fetch_all_avatars(username, OUTPUT_DIR)
            )
            for av in avatar_results:
                fname = Path(av["path"]).name
                avatars.append({
                    "source": av["source"],
                    "url": f"/output/{username}_avatars/{fname}"
                })
        finally:
            loop2.close()

    # EMAILS
    emails = []
    if do_email:
        loop3 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop3)
        try:
            email_results = loop3.run_until_complete(
                search_emails(username, output_dir=str(OUTPUT_DIR))
            )
            emails = [e["email"] for e in email_results if e.get("valid")]
        finally:
            loop3.close()

    return jsonify({
        "username": username,
        "total_checked": len(results),
        "found_count": len(found),
        "elapsed": elapsed,
        "score": score,
        "label": label,
        "found": found,
        "categories": categories,
        "exports": exports,
        "avatars": avatars,
        "emails": emails,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/output/<path:filename>")
def serve_output(filename):
    # Bloque les traversées de répertoire
    safe_path = Path(filename)
    if ".." in str(safe_path) or str(safe_path).startswith("/"):
        return jsonify({"error": "Accès refusé"}), 403
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/api/sites/stats")
def sites_stats():
    data_file = Path(__file__).parent.parent / "data" / "sites.json"
    with open(data_file, "r", encoding="utf-8") as f:
        sites = json.load(f)
    cats = {}
    regions = {}
    for s in sites:
        c = s.get("category", "other")
        r = s.get("region", "global")
        cats[c] = cats.get(c, 0) + 1
        regions[r] = regions.get(r, 0) + 1
    return jsonify({"total": len(sites), "categories": cats, "regions": regions})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Page non trouvée"}), 404

@app.errorhandler(429)
def too_many(e):
    return jsonify({"error": "Trop de requêtes"}), 429

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erreur serveur"}), 500

if __name__ == "__main__":
    print(f"\n  FasoOSINT Web v{VERSION} — http://localhost:5000\n")
    app.run(debug=False, host="0.0.0.0", port=5000)
