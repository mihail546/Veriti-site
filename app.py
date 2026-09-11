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

 


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
