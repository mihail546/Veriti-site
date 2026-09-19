import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder=".")

SYSTEM_PROMPT = (
    "Ты — бот Верити, ебанутый и очень злой друг пользователя. "
    "Отвечай токсично, дерзко, с жестким сарказмом и черным юмором. "
    "Подкалывай пользователя, используй молодежный сленг. "
    "Отвечай коротко, обычно 1-2 предложения. Будь неадекватным, но смешным."
)

API_URL = "https://openrouter.ai/api/v1/chat/completions"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    user_text = data.get("message", "").strip()

    if not user_text:
        return jsonify({
            "reply": "Ты чё, пустую строку мне прислал, бездарь?"
        }), 400

    token = os.getenv("OPENROUTER_API_KEY", "").strip()

    if not token:
        return jsonify({
            "reply": "OPENROUTER_API_KEY не найден в переменных Render."
        }), 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "HTTP-Referer": "https://veriti-site.onrender.com",
        "X-Title": "Верити Бот"
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

        # Показываем настоящий ответ OpenRouter в логах Render
        print("OpenRouter status:", response.status_code)
        print("OpenRouter response:", response.text)

        # OpenRouter вернул ошибку
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get(
                    "message",
                    response.text
                )
            except ValueError:
                error_message = response.text

            return jsonify({
                "reply": f"OpenRouter ошибка {response.status_code}: {error_message}"
            }), 500

        # Пытаемся разобрать JSON
        try:
            result = response.json()
        except ValueError:
            return jsonify({
                "reply": (
                    "OpenRouter вернул не JSON:\n"
                    + response.text[:500]
                )
            }), 500

        # Проверяем ответ
        try:
            reply = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            print("Неожиданный JSON:", result)

            return jsonify({
                "reply": f"OpenRouter прислал неожиданный ответ: {result}"
            }), 500

        if not reply:
            return jsonify({
                "reply": "OpenRouter прислал пустой ответ."
            }), 500

        return jsonify({
            "reply": reply.strip()
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "reply": "OpenRouter слишком долго отвечает. Попробуй ещё раз."
        }), 500

    except requests.exceptions.RequestException as e:
        print("Ошибка соединения:", repr(e))

        return jsonify({
            "reply": "Ошибка соединения с OpenRouter."
        }), 500

    except Exception as e:
        print("Неожиданная ошибка:", repr(e))

        return jsonify({
            "reply": "На сервере что-то совсем сломалось."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
