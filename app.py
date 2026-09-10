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
        
        # Если статус 200 — всё отлично
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                reply = res_json[0].get("generated_text", "").replace("<|im_end|>", "").strip()
                if reply:
                    return jsonify({"reply": reply})

        # Если HF вернул ошибку — выводим её КОД и ТЕКСТ прямо в чат
        return jsonify({"reply": f"Ошибка HF [{response.status_code}]: {response.text}"}), 500

    except Exception as e:
        # Если упало само соединение в Python — выводим детали исключения
        return jsonify({"reply": f"Ошибка Python-запроса: {str(e)}"}), 500
