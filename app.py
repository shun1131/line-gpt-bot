from flask import Flask, request
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# OpenAIクライアントの初期化（v1.xの書き方）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json

    for event in body.get("events", []):
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        user_msg = event["message"]["text"]
        reply_token = event["replyToken"]

        # ChatGPTに投げる（v1.xの書き方）
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_msg}
                ],
                timeout=10
            )
            reply_text = response.choices[0].message.content
        except Exception as e:
            reply_text = f"ごめんね、ちょっとエラーが出ちゃったみたい🥲\n{str(e)}"

        # LINEに返信
        reply(reply_token, reply_text)

    return "OK", 200

def reply(token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
