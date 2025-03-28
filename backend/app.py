from flask import Flask, request, jsonify, render_template, session
import requests
import json
import os
import urllib.parse
from statistics import mean
from flask_cors import CORS
from uuid import uuid4

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY", str(uuid4()))

server_map = {
    "백호": 1,
    "주작": 2,
    "현무": 3,
    "청룡": 4
}

ALERT_KEYWORDS_FILE = "alert_keywords.json"

def load_alert_keywords():
    if os.path.exists(ALERT_KEYWORDS_FILE):
        with open(ALERT_KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_alert_keywords(keywords):
    with open(ALERT_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    exact = request.args.get("exact", "false").lower() == "true"
    server = request.args.get("server", "백호")
    server_id = server_map.get(server, 1)

    print(f"[🔍 검색 요청] keyword='{keyword}', server='{server}'")

    params = {"page": 0, "size": 20}
    if keyword:
        params["itemName"] = keyword

    try:
        res = requests.get(
            f"https://api.gersanginfo.com/api/market/{server_id}/search",
            params=params,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        res.raise_for_status()
        data = res.json().get("content", [])
    except Exception as e:
        print("[ERROR]", e)
        return jsonify([])

    results = []
    for item in data:
        name = item.get("itemName", "")
        if keyword and exact and name != keyword:
            continue
        results.append({
            "itemName": name,
            "characterName": item.get("nickname", "이름없음"),
            "quantity": item.get("quantity", 1),
            "price": item.get("price", 0)
        })

    return jsonify(results)

@app.route("/alert-keywords", methods=["GET", "POST", "DELETE"])
def alert_keywords():
    if request.method == "GET":
        return jsonify(load_alert_keywords())

    keywords = load_alert_keywords()
    data = request.json
    keyword = data.get("keyword", "").strip()

    if request.method == "POST":
        if keyword and keyword not in keywords:
            keywords.append(keyword)
            save_alert_keywords(keywords)
        return jsonify({"status": "added", "keywords": keywords})

    elif request.method == "DELETE":
        if keyword in keywords:
            keywords.remove(keyword)
            save_alert_keywords(keywords)
        return jsonify({"status": "deleted", "keywords": keywords})

@app.route("/saton")
def saton():
    return render_template("saton.html")

@app.route("/proxy-saton")
def proxy_saton():
    server_id = request.args.get("server", "3")
    content = request.args.get("content", "")
    base_url = f"https://api.gersanginfo.com/api/global-message/{server_id}/search"
    params = f"?page=0&size=50"

    if content:
        encoded = urllib.parse.quote(content)
        params += f"&content={encoded}"

    url = base_url + params
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
