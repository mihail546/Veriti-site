import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder=".")

SYSTEM_PROMPT = (
    "Ты — бот Верити, дерзкий и саркастичный друг пользователя. "
    "Отвечай коротко, обычно 1-2 предложения, с юмором и молодежным сленгом. "
    "Не переходи на реальные угрозы, травлю или опасные советы."
)

API_URL = "https://openrouter.ai/api/v1/chat/completions"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    user_text = str(data.get("message", "")).strip()

    if not user_text:
        return jsonify({
            "reply": "Ты отправил пустое сообщение 😭"
        }), 400

    token = os.getenv("OPENROUTER_API_KEY", "").strip()

    if not token:
        return jsonify({
            "reply": "OPENROUTER_API_KEY не найден в переменных окружения."
        }), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv(
            "APP_URL",
            "http://localhost:5000"
        ),
        "X-Title": "Верити Бот",
    }

    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        "max_tokens": 150,
        "temperature": 0.8
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        # Очень важно: показываем реальную ошибку OpenRouter
        if not response.ok:
            try:
                error_data = response.json()
                error_message = (
                    error_data.get("error", {}).get("message")
                    or str(error_data)
                )
            except ValueError:
                error_message = response.text[:500]

            print(
                f"OpenRouter error {response.status_code}: "
                f"{error_message}"
            )

            return jsonify({
                "reply": (
                    f"OpenRouter вернул ошибку "
                    f"{response.status_code}: {error_message}"
                )
            }), 502

        result = response.json()

        choices = result.get("choices", [])

        if not choices:
            print("Unexpected API response:", result)

            return jsonify({
                "reply": "API вернул ответ без choices."
            }), 502

        message = choices[0].get("message", {})
        reply = message.get("content")

        if not reply:
            print("Unexpected API response:", result)

            return jsonify({
                "reply": "API не вернул текст ответа."
            }), 502

        return jsonify({
            "reply": reply.strip()
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "reply": "OpenRouter слишком долго отвечает."
        }), 504

    except requests.exceptions.RequestException as e:
        print("Request error:", repr(e))

        return jsonify({
            "reply": "Не удалось подключиться к OpenRouter."
        }), 502

    except ValueError:
        return jsonify({
            "reply": "OpenRouter вернул некорректный JSON."
        }), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
