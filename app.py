import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='.')

SYSTEM_PROMPT = (
    "Ты — бот Верити, ебанутый и очень злой друг пользователя. Твоя задача — "
    "отвечать токсично, дерзко, с жестким сарказмом и черным юмором. "
    "Подкалывай пользователя, называй его бездарем, отвечай коротко (1-2 предложения) "
    "и используй молодежный сленг. Будь неадекватным, но смешным."
)

# === OPENROUTER API ===
API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    
    if not user_text:
        return jsonify({"reply": "Ты чё, пустую строку мне прислал, бездарь?"}), 400

    token = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not token:
        return jsonify({"reply": "Бездарь, ты забыл указать OPENROUTER_API_KEY в переменных окружения!"}), 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "HTTP-Referer": "https://veriti-site.onrender.com/", 
        "X-Title": "veritybot"
    }

    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free", 
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 100,
        "temperature": 0.8
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code != 200:
            return jsonify({"reply": f"Сервер загнулся. Ошибка API: {response.status_code}"}), 500

        result = response.json()
        reply = result['choices'][0]['message']['content'].strip()
        return jsonify({"reply": reply})

    except requests.exceptions.RequestException:
        return jsonify({"reply": "Ошибка соединения с API. Давай по новой, бездарь."}), 500
    except (KeyError, IndexError):
        return jsonify({"reply": "Пришел корявый ответ от ИИ."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
