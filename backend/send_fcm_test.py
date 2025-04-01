import requests
import json

# ① 너의 FCM 서버 키 (절대 외부에 노출하지 마!)
server_key = "66f8ff8cbe4b9663ab31dd9cf1ffb4dc65fd71c9"  # 🔒 여기에 너의 키 전체를 넣기

# ② 아까 받은 FCM 토큰
target_token = "fq3RCQE0TLq54BEGl6Z5g9:APA91bGkohz5gkzj_ecZO_KZzYxKPsq2ObKRDV9FmPnPrrq6DE91NDDByh9F1kWDsLU5HFM3R9vq6e2wU0LUQLmpO3dJr2wB0yf3Ctp7pWdWA-WEQPcGo0U"
  # 🔒 토큰 전체

# ③ 보낼 메시지
message = {
    "to": target_token,
    "notification": {
        "title": "🔥 테스트 알림",
        "body": "백그라운드에서도 잘 오나요?"
    },
    "priority": "high"
}

# ④ 전송 요청
headers = {
    "Content-Type": "application/json",
    "Authorization": "key=" + server_key
}

response = requests.post("https://fcm.googleapis.com/fcm/send",
                         headers=headers, data=json.dumps(message))

print("✅ 응답 코드:", response.status_code)
print("📬 응답 내용:", response.text)
