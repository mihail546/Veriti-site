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
    
    # Прямой и стабильный шлюз к мощному бесплатному ИИ
    api_url = "https://huggingface.co"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{user_text}<|im_end|>\n<|im_start|>assistant\n"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100, "temperature": 0.85}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        res_json = response.json()
        if isinstance(res_json, list) and "generated_text" in res_json[0]:
            full_text = res_json[0]["generated_text"]
            reply = full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
            if reply:
                return jsonify({"reply": reply})
    except:
        pass
        
    return jsonify({"reply": "я не знаю, но что то случится через 3 дня."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
