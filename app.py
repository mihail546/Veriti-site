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

# Используем конкретную модель Llama 3
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

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
    
    # Если заведёшь бесплатный токен на Hugging Face (https://huggingface.co/settings/tokens),
    # раскомментируй строчку ниже и вставь его сюда для снятия жестких лимитов:
    # headers["Authorization"] = "Bearer hf_ваштокенизнастроек"

    # Форматируем промпт под Llama-3
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{SYSTEM_PROMPT}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n{user_text}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.8,
            "return_full_text": False  # Возвращать только новый текст ответа
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=10)
        
        # Успешный ответ
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                reply = res_json[0].get("generated_text", "").replace("<|eot_id|>", "").strip()
                if reply:
                    return jsonify({"reply": reply})

        # Если модель ещё грузится (503 Service Unavailable)
        if response.status_code == 503:
            return jsonify({"reply": "Модель ещё просыпается, подожди 10 секунд и спроси снова."}), 503

        # Вывод ошибки в терминал для отладки
        print(f"[HF ERROR] Статус: {response.status_code}, Ответ: {response.text}")
        return jsonify({"reply": "Сервер ИИ приуныл или заблокировал запрос."}), 500

    except requests.exceptions.Timeout:
        print("[ERROR] Превышено время ожидания ответа от HF")
        return jsonify({"reply": "Таймаут соединения, ИИ слишком долго тупил."}), 504
        
    except Exception as e:
        print(f"[ERROR] Исключение: {e}")
        return jsonify({"reply": "Ошибка сети при попытке достучаться до сервера."}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
