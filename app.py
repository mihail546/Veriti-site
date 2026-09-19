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

API_URL = "https://openrouter.ai/api/v1/chat/completions"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(silent=True) or {}
        user_text = data.get("message", "").strip()

        if not user_text:
            return jsonify({
                "reply": "Ты чё, пустую строку мне прислал, бездарь?"
            }), 400

        token = os.getenv("OPENROUTER_API_KEY", "").strip()

        if not token:
            return jsonify({
                "reply": "OPENROUTER_API_KEY не найден в Render."
            }), 500

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "HTTP-Referer": "https://veriti-site.onrender.com",
            "X-Title": "Veriti Bot"
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

        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("OpenRouter STATUS:", response.status_code)
        print("OpenRouter RESPONSE:", response.text)

        if response.status_code != 200:
            try:
                error_data = response.json()
                error = error_data.get("error", {})
                
                if isinstance(error, dict):
                    message = error.get("message", str(error))
                else:
                    message = str(error)

            except Exception:
                message = response.text[:500]

            return jsonify({
                "reply": f"OpenRouter ошибка {response.status_code}: {message}"
            }), 500

        try:
            result = response.json()
        except Exception:
            return jsonify({
                "reply": "OpenRouter вернул не JSON."
            }), 500

        choices = result.get("choices")

        if not choices:
            return jsonify({
                "reply": f"В ответе нет choices: {result}"
            }), 500

        message = choices[0].get("message", {})
        reply = message.get("content")

        if not reply:
            return jsonify({
                "reply": f"OpenRouter не прислал текст: {result}"
            }), 500

        return jsonify({
            "reply": reply.strip()
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "reply": "OpenRouter слишком долго отвечает."
        }), 500

    except requests.exceptions.RequestException as e:
        print("REQUEST ERROR:", repr(e))

        return jsonify({
            "reply": f"Ошибка соединения: {e}"
        }), 500

    except Exception as e:
        print("UNKNOWN ERROR:", repr(e))

        return jsonify({
            "reply": f"Ошибка сервера: {type(e).__name__}: {e}"
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
