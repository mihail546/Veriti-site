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
    
    # Прямой безлимитный шлюз к ИИ без ключей и ошибок
    url = "https://huggingface.co"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "inputs": f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "parameters": {"max_new_tokens": 80, "temperature": 0.9}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and "generated_text" in res_json[0]:
                full_text = res_json[0]["generated_text"]
                # Вырезаем только чистый текст ответа ИИ
                reply = full_text.split("<|start_header_id|>assistant<|end_header_id|>\n\n")[-1].replace("<|eot_id|>", "").strip()
                if reply:
                    return jsonify({"reply": reply})
    except:
        pass
        

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
