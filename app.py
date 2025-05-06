from flask import Flask, request, abort
import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json

    for event in body.get("events", []):
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        user_msg = event["message"]["text"]
        reply_token = event["replyToken"]

        # ChatGPTに投げる
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # gpt-4にしてもOK
            messages=[
                {"role": "user", "content": user_msg}
            ]
        )
        reply_text = res["choices"][0]["message"]["content"]

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
