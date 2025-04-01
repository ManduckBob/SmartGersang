from flask import Flask, request, jsonify, render_template
import requests
import json
import os
import urllib.parse
from flask_cors import CORS
from uuid import uuid4
from google.oauth2 import service_account
import google.auth.transport.requests
from dotenv import load_dotenv

# ✅ 환경변수 로딩
load_dotenv()

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

# ✅ FCM 알림 전송 함수
def send_fcm_notification(target_token, title, body):
    service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    project_id = 'smartgersang'
    scopes = ['https://www.googleapis.com/auth/firebase.messaging']

    try:
        if not service_account_info:
            raise Exception("환경변수 'GOOGLE_SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

        credentials = service_account.Credentials.from_service_account_info(
            json.loads(service_account_info), scopes=scopes
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        url = f'https://fcm.googleapis.com/v1/projects/{project_id}/messages:send'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }
        message = {
            "message": {
                "token": target_token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(message))
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }

    except Exception as e:
        return {
            "status_code": 500,
            "error": str(e)
        }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/saton")
def saton():
    return render_template("saton.html")

@app.route("/proxy-saton")
def proxy_saton():
    server_id = request.args.get("server", "3")
    content = request.args.get("content", "")
    base_url = f"https://api.gersanginfo.com/api/global-message/{server_id}/search"
    params = "?page=0&size=50"

    if content:
        encoded = urllib.parse.quote(content)
        params += f"&content={encoded}"

    url = base_url + params
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        messages = data.get("content", [])

        keywords = load_alert_keywords()
        target_token = os.environ.get("FCM_TARGET_TOKEN")

        for msg in messages:
            message_text = msg.get("content", "")
            for keyword in keywords:
                if keyword in message_text:
                    print(f"[📨 키워드 감지] '{keyword}' in '{message_text}'")
                    send_fcm_notification(target_token, "새 메시지 감지", message_text)
                    break

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    exact = request.args.get("exact", "false").lower() == "true"
    server = request.args.get("server", "백호")
    server_id = server_map.get(server, 1)

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
