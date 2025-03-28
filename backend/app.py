from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import urllib.parse
from statistics import mean

app = Flask(__name__)

server_map = {
    "백호": 1,
    "주작": 2,
    "현무": 3,
    "청룡": 4
}

WATCHLIST_FILE = "watchlist.json"
ALERT_KEYWORDS_FILE = "alert_keywords.json"

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=2)

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
    watchlist = load_watchlist()
    analyzed = []

    for item in watchlist:
        server = item["server"]
        keyword = item["item"]
        server_id = server_map.get(server, 1)

        try:
            res = requests.get(f"https://api.gersanginfo.com/api/market/{server_id}/search",
                               params={"page": 0, "size": 100, "itemName": keyword},
                               headers={"User-Agent": "Mozilla/5.0"})
            data = res.json().get("content", [])

            prices = []
            lowest = None

            for entry in data:
                price = entry.get("price", 0)
                quantity = entry.get("quantity", 1)
                name = entry.get("itemName", keyword)
                item["item"] = name  # 최신 이름 저장

                prices.append(price)
                if quantity >= 100:
                    if lowest is None or price < lowest:
                        lowest = price

            if not lowest and prices:
                lowest = min(prices)

            avg = int(mean(prices)) if prices else None

            analyzed.append({
                "item": item["item"],
                "server": server,
                "lowest": lowest,
                "average": avg
            })

        except Exception as e:
            print(f"[ERROR] 분석 실패: {e}")

    return render_template("index.html", watchlist=watchlist, analyzed=analyzed)

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

@app.route("/watchlist", methods=["POST", "DELETE"])
def update_watchlist():
    data = request.json
    item = data.get("item")
    server = data.get("server")
    watchlist = load_watchlist()

    if request.method == "POST":
        for entry in watchlist:
            if entry["item"] == item and entry["server"] == server:
                return jsonify({"status": "already exists"})
        watchlist.append({"item": item, "server": server})
        save_watchlist(watchlist)
        return jsonify({"status": "added"})

    elif request.method == "DELETE":
        watchlist = [w for w in watchlist if not (w["item"] == item and w["server"] == server)]
        save_watchlist(watchlist)
        return jsonify({"status": "deleted"})

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
    port = int(os.environ.get("PORT", 5000))  # Render가 할당해주는 포트를 사용
    app.run(host="0.0.0.0", port=port)