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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    
    if not user_text:
        return jsonify({"reply": "Ты чё, пустую строку мне прислал, бездарь?"}), 400

    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        return jsonify({"reply": "Бездарь, ты забил указать HF_TOKEN в настройках Render!"}), 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

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
        
        if response.status_code == 200:
            res_json = response.json()
            choices = res_json.get('choices', [])
            if choices:
                reply = choices[0].get('message', {}).get('content', '').strip()
                if reply:
                    return jsonify({"reply": reply})

        return jsonify({"reply": f"HF Error [{response.status_code}]: {response.text}"}), 200

    except Exception as e:
        return jsonify({"reply": f"Python Error: {str(e)}"}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
