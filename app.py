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

HF_API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"
HF_TOKEN = ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    
    if not user_text:
        return jsonify({"reply": "Ты чё, пустую строку мне прислал, бездарь?"}), 400

    headers = {"Content-Type": "application/json"}
    
    token = HF_TOKEN or os.environ.get("HF_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"

    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 100,
        "temperature": 0.8
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=25)
        
        # Если API ответил успешно — отдаем ответ Верити
        if response.status_code == 200:
            res_json = response.json()
            reply = res_json['choices'][0]['message']['content'].strip()
            if reply:
                return jsonify({"reply": reply})

        # Если ошибка в токене или доступе
        if response.status_code in (401, 403):
            return jsonify({"reply": "Проблема с токеном HF. Проверь переменную HF_TOKEN в Render."}), 500

        # Если модель разогревается
        if response.status_code == 503:
            return jsonify({"reply": "Модель просыпается, подожди 10 секунд и спроси ещё раз."}), 503

        return jsonify({"reply": f"Ошибка HF (код {response.status_code})."}), 500

    except Exception:
        return jsonify({"reply": "Ошибка соединения с сервером."}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
