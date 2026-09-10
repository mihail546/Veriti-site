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
            reply = res_json['choices'][0]['message']['content'].strip()
            if reply:
                return jsonify({"reply": reply})

        return jsonify({"reply": f"Ошибка HF [{response.status_code}]: {response.text}"}), 500

    except Exception as e:
        return jsonify({"reply": f"Ошибка Python-запроса: {str(e)}"}), 500
