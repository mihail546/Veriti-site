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
    
    # Подключаем стабильный бесплатный шлюз ИИ, устойчивый к блокировкам
    url = "https://groq.com"
    
    # Используем общедоступный ключ для тестов разработки
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.85,
        "max_tokens": 120
    }
    
    try:
        # Прямой запрос к высокоскоростному облаку ИИ
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        res_json = response.json()
        
        if response.status_code == 200 and "choices" in res_json:
            reply = res_json["choices"][0]["message"]["content"].strip()
            if reply:
                return jsonify({"reply": reply})
                
        # Если сервер ИИ вернул ошибку — выводим её текст на сайт вместо заглушки
        return jsonify({"reply": f"Ошибка сервера ИИ (Код {response.status_code}): {response.text[:100]}"})
    except Exception as e:
        # Если упала сама сеть — выводим системную ошибку
        return jsonify({"reply": f"Системная ошибка сети: {str(e)[:100]}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
