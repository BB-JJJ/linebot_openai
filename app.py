from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 加入計數器
counter = {"count": 0}

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text1 = event.message.text.strip().lower()

    # 檢查是否為「查看計數」指令
    if text1 in ['count', '查看計數', '訊息數', '訊息總數']:
        ret = f"目前已傳送 OpenAI 訊息次數：{counter['count']} 次"
    else:
        # 正常走 OpenAI 回應流程
        response = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": text1}],
            model="gpt-4o-mini-2024-07-18",
            temperature=0.5,
        )
        try:
            ret = response['choices'][0]['message']['content'].strip()
            counter["count"] += 1
            print(f"[計數器] 已處理訊息數量：{counter['count']}")
        except:
            ret = '發生錯誤！'

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
