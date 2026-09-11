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

# Актуальный эндпоинт Hugging Face
HF_API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"
HF_TOKEN = "" # Токен берется из Environment Variables на Render

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

 


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
