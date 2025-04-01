import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# 🔑 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_FILE = 'smartgersang-firebase-adminsdk-fbsvc-324fd474b9.json'  # 네가 받은 JSON 파일 이름

# ✅ FCM 프로젝트 ID
PROJECT_ID = 'smartgersang'  # Firebase 콘솔에서 확인 가능

# 🔔 타겟 디바이스 토큰
target_token = 'fq3RCQE0TLq54BEGl6Z5g9:APA91bGkohz5gkzj_ecZO_KZzYxKPsq2ObKRDV9FmPnPrrq6DE91NDDByh9F1kWDsLU5HFM3R9vq6e2wU0LUQLmpO3dJr2wB0yf3Ctp7pWdWA-WEQPcGo0U'

# 🔐 권한 범위
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# 📡 인증 및 토큰 발급
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
access_token = credentials.token

# 📨 FCM 메시지 전송
url = f'https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json; UTF-8',
}
message = {
    "message": {
        "token": target_token,
        "notification": {
            "title": "📬 소식!",
            "body": "백그라운드 알림 테스트입니다 😎"
        }
    }
}
response = requests.post(url, headers=headers, data=json.dumps(message))

print("✅ 응답 코드:", response.status_code)
print("📬 응답 내용:", response.text)
