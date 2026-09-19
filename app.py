import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder=".")

SYSTEM_PROMPT = (
    "Ты — бот Верити, ебанутый и очень злой друг пользователя. "
    "Отвечай токсично, дерзко, с сарказмом и черным юмором. "
    "Подкалывай пользователя, используй молодежный сленг. "
    "Отвечай коротко, обычно 1-2 предложения. Будь смешным."
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    text = data.get("message", "").strip()

    if not text:
        return jsonify({"reply": "Ты чё, пустую строку прислал, бездарь?"}), 400

    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return jsonify({"reply": "OPENROUTER_API_KEY не найден в Render."}), 500

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "Veriti Bot"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "max_tokens": 500,
        "temperature": 0.8,
        "reasoning": {"enabled": False}
    }

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        data = r.json()

        if r.status_code != 200:
            error = data.get("error", {}).get("message", "Неизвестная ошибка")
            return jsonify({"reply": f"OpenRouter: {error}"}), 500

        reply = data["choices"][0]["message"].get("content")

        if not reply:
            return jsonify({"reply": "Модель не прислала текст 😭"}), 500

        return jsonify({"reply": reply.strip()})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": f"Ошибка сервера: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
