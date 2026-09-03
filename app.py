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
    
    # Полностью свободный и бесплатный прокси-хаб без проверки возраста
    url = "https://aryahcr.cc"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "model": "gpt-4",
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        res_json = response.json()
        
        # Извлекаем текст ответа из прокси
        if response.status_code == 200 and "gpt" in res_json:
            reply = res_json["gpt"].strip()
            if reply:
                return jsonify({"reply": reply})
                
        return jsonify({"reply": f"Ошибка ИИ (Код {response.status_code})" })
    except Exception as e:
        return jsonify({"reply": f" Ошибка сети сервера" })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
