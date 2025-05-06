from flask import Flask, request
import openai
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json

    for event in body.get("events", []):
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        user_msg = event["message"]["text"]
        reply_token = event["replyToken"]

        # ChatGPTに投げる
        try:
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_msg}],
                timeout=10
            )
            reply_text = res["choices"][0]["message"]["content"]
        except Exception as e:
            reply_text = f"ごめんね、ちょっとエラーが出ちゃったみたい🥲\n{e}"

        # LINEに返す
        reply(reply_token, reply_text)

    return "OK", 200

def reply(token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
