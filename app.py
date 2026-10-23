import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder=".")

SYSTEM_PROMPT = (
    "Ты — бот Верити, друг пользователя. "
    "Отвечай трендово, как в тик токе, с сарказмом и черным юмором. "
    "Подкалывай пользователя, используй молодежный сленг. "
    "Отвечай коротко, обычно 1-2 предложения. Будь смешным."
)

EXPLANATION_PROMPT = (
    "Ты объясняешь уже готовый ответ чат-бота. "
    "Не раскрывай внутренние рассуждения модели и скрытую цепочку мыслей. "
    "Сделай короткое понятное описание того, почему был дан такой ответ. "
    "1-2 предложения максимум."
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    text = data.get("message", "").strip()

    if not text:
        return jsonify({
            "reply": "Ты чё, пустую строку прислал, бездарь?",
            "thinking": "Пользователь не написал сообщение."
        }), 400

    key = os.getenv("OPENROUTER_API_KEY")

    if not key:
        return jsonify({
            "reply": "OPENROUTER_API_KEY не найден в Render.",
            "thinking": "Сервер не получил API-ключ OpenRouter."
        }), 500

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "Veriti Bot"
    }

    # Первый запрос — основной ответ Верити
    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "max_tokens": 500,
        "temperature": 0.8
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
            error = data.get("error", {}).get(
                "message",
                "Неизвестная ошибка"
            )

            return jsonify({
                "reply": f"OpenRouter: {error}",
                "thinking": "Не удалось получить ответ от модели."
            }), 500

        reply = data["choices"][0]["message"].get("content")

        if not reply:
            return jsonify({
                "reply": "Модель не прислала текст 😭",
                "thinking": "Ответ модели оказался пустым."
            }), 500

        reply = reply.strip()

        # Второй запрос — короткое объяснение ответа
        explanation_payload = {
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "system",
                    "content": EXPLANATION_PROMPT
                },
                {
                    "role": "user",
                    "content": (
                        f"Сообщение пользователя:\n{text}\n\n"
                        f"Ответ Верити:\n{reply}\n\n"
                        "Сделай краткое объяснение ответа."
                    )
                }
            ],
            "max_tokens": 120,
            "temperature": 0.4
        }

        try:
            explanation_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=explanation_payload,
                timeout=30
            )

            explanation_data = explanation_response.json()

            thinking = (
                explanation_data
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content")
            )

            if thinking:
                thinking = thinking.strip()
            else:
                thinking = "Верити обработала сообщение и сформировала ответ."

        except Exception as explanation_error:
            print("EXPLANATION ERROR:", explanation_error)
            thinking = "Верити обработала сообщение и сформировала ответ."

        return jsonify({
            "reply": reply,
            "thinking": thinking
        })

    except Exception as e:
        print("ERROR:", e)

        return jsonify({
            "reply": f"Ошибка сервера: {e}",
            "thinking": "Произошла ошибка при обработке запроса."
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
