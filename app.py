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

HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
HF_TOKEN = ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_text = data.get('message', '').strip()
    
    if not user_text:
        return jsonify({"reply": "Пустой запрос!"}), 400

    headers = {"Content-Type": "application/json"}
    
    token = HF_TOKEN or os.environ.get("HF_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"

    prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.8,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=25)
        
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                reply = res_json[0].get("generated_text", "").replace("<|im_end|>", "").strip()
                if reply:
                    return jsonify({"reply": reply})

        return jsonify({"reply": f"Ошибка HF [{response.status_code}]: {response.text}"}), 500

    except Exception as e:
        return jsonify({"reply": f"Ошибка Python-запроса: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
