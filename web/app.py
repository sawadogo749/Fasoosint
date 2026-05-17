#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import json
import time
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

sys.path.insert(0, str(Path(__file__).parent.parent))
from fasoosint import run_search, save_html, save_csv, save_txt, VERSION

app = Flask(__name__)
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html", version=VERSION)

@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json()
    username = data.get("username", "").strip()
    lang = data.get("lang", "fr")
    region = data.get("region") or None
    category = data.get("category") or None
    timeout = int(data.get("timeout", 10))
    concurrency = int(data.get("concurrency", 50))
    export_html = data.get("export_html", False)
    export_csv = data.get("export_csv", False)

    if not username:
        return jsonify({"error": "Username requis"}), 400
    if len(username) > 50:
        return jsonify({"error": "Username trop long"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results, found, elapsed = loop.run_until_complete(
            run_search(username, lang, concurrency=concurrency,
                       filter_region=region, filter_category=category,
                       timeout=timeout)
        )
    finally:
        loop.close()

    exports = []
    if export_html:
        save_html(username, found, results, lang, OUTPUT_DIR, elapsed)
        exports.append(f"/output/{username}_fasoosint.html")
    if export_csv:
        save_csv(username, results, lang, OUTPUT_DIR)
        exports.append(f"/output/{username}_fasoosint.csv")
    save_txt(username, found, lang, OUTPUT_DIR)
    exports.append(f"/output/{username}_fasoosint.txt")

    categories = {}
    for r in found:
        cat = r.get("category") or "other"
        categories.setdefault(cat, []).append(r)

    return jsonify({
        "username": username,
        "total_checked": len(results),
        "found_count": len(found),
        "elapsed": elapsed,
        "found": found,
        "categories": categories,
        "exports": exports,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/output/<path:filename>")
def serve_output(filename):
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

if __name__ == "__main__":
    print(f"\n  FasoOSINT Web v{VERSION} — http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
