import os
import json
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='.')

SYSTEM_PROMPT = (
    "Ты — бот Верити, ебанутый и очень злой друг пользователя. Твоя задача — отвечать "
    "на любые вопросы токсично, дерзко, с жестким сарказмом и черным юмором. "
    "Подкалывай пользователя, называй его бездарем, отвечай коротко (1-2 предложения) "
    "и используй молодежный сленг. Будь неадекватным, но смешным."
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_text = data.get('message', '')

    url = "https://duckduckgo.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/event-stream",
        "x-vqd-4": "1"
    }
    
    try:
        init_res = requests.get("https://duckduckgo.com", headers={"x-vqd-4": "1"})
        vqd = init_res.headers.get("x-vqd-4")
        
        if vqd:
            headers["x-vqd-4"] = vqd
            res = requests.post(
                url,
                headers=headers,
                json={
                    "model": "meta-llama/Meta-Llama-3-70B-Instruct",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_text}
                    ]
                },
                timeout=8
            )
            
            if res.status_code == 200:
                full_reply = ""
                for line in res.text.split("\n"):
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "message" in chunk:
                                full_reply += chunk["message"]
                        except:
                            pass
                
                if full_reply:
                    return jsonify({"reply": full_reply.strip()})
    except:
        pass

    return jsonify({"reply": "я не знаю, но что то случится через 3 дня."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
