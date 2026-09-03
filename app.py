import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='.')

SYSTEM_PROMPT = (
    "Ты — бот Верити, ебанутый и очень злой друг пользователя. Твоя задача — "
    "отвечать токсично, дерзко, с жестким сарказмом и черным юмором. "
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
    
    # Стабильный шлюз, который не блокирует запросы от облачных серверов Render
    url = "https://adventblocks.cc"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer free-chimera-key-is-not-needed-here"
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai",
            headers={"Content-Type": "application/json"},
            json={
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=10
        )
        if response.status_code == 200:
            res_json = response.json()
            reply = res_json["choices"][0]["message"]["content"].strip()
            if reply:
                return jsonify({"reply": reply})
    except:
        pass
        
    return jsonify({"reply": "я не знаю, но что то случится через 3 дня."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
