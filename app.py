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
    
    # Сверхбыстрый и безотказный шлюз, полностью открытый для серверов Render
    url = "https://atoma.cloud"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer atoma-free- шлюз-для-разработки-сайтов"
    }
    
    payload = {
        "model": "meta-llama/meta-llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.85,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        
        if response.status_code == 200:
            res_json = response.json()
            if "choices" in res_json and len(res_json["choices"]) > 0:
                reply = res_json["choices"][0]["message"]["content"].strip()
                if reply:
                    return jsonify({"reply": reply})
                    
        return jsonify({"reply": f"Ошибка ИИ (Код {response.status_code})" or "Пустой ответ сервера."})
    except Exception as e:
        return jsonify({"reply": f"Ошибка сети: {str(e)[:40]}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
