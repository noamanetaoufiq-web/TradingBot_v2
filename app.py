import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Configuration dyalk ---
TELEGRAM_TOKEN = '8678024978:AAHBJ16lzA5MaaBLA-8Z15nwDJV5BLGq-Zw'
USER_ID = 'noamane_dev'  # L-ID dyalk
OPENROUTER_KEY = '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'

STRATEGY_RULES = """
Analyze the incoming market signal based on Noamane's Strategy:
1. Uptrend: 1st Entry Long -> Pullback -> 2nd Entry Long (BUY).
2. Downtrend: 1st Entry Short -> Pullback -> 2nd Entry Short (SELL).
3. Failures: 
   - 2nd Entry Short failing in Uptrend = Strong BUY.
   - 2nd Entry Long failing in Downtrend = Strong SELL.
Context: Price must be near EMA. 
Output: Brief advice in Moroccan Darija.
"""

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": f"@{USER_ID}", "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # TradingView ghadi y-sift JSON
    if not data:
        return "No Data", 400

    # Sift l-data l-AI (OpenRouter)
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    ai_payload = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [
            {"role": "system", "content": STRATEGY_RULES},
            {"role": "user", "content": f"Market Data: {data}"}
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=ai_payload)
        ai_advice = response.json()['choices'][0]['message']['content']
        
        # Sift l-natija l-Telegram dyalk
        full_msg = f"🚀 **New Signal!**\n\n{ai_advice}"
        send_telegram_msg(full_msg)
        return "Success", 200
    except Exception as e:
        send_telegram_msg(f"❌ Error f-l-AI: {str(e)}")
        return "Error", 500

if __name__ == '__main__':
    # Render kiy-htaj l-Port y-koun dynamique
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)