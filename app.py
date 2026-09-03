import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Промпт без упоминания АП, характер злой и угарный, как ты и хотел
SYSTEM_PROMPT = (
    "Ты — бот Верити, ебанутый и очень злой друг пользователя. Твоя задача — отвечать "
    "на любые вопросы токсично, дерзко, с жестким сарказмом и черным юмором. "
    "Подкалывай пользователя, называй его бездарем, отвечай коротко (1-2 предложения) "
    "и используй молодежный сленг. Будь неадекватным, но смешным."
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Верити — Твой Друг</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: #121212; 
            color: #e0e0e0; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            min-height: 100vh;
            padding: 20px;
        }
        h2 {
            color: #ffcc00;
            margin-bottom: 15px;
            font-size: 24px;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(255, 204, 0, 0.3);
        }
        #chat-container { 
            width: 100%; 
            max-width: 550px; 
            background: #1e1e1e; 
            border-radius: 16px; 
            overflow: hidden; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.7);
            border: 1px solid #2d2d2d;
        }
        #chat-window { 
            height: 450px; 
            padding: 20px; 
            overflow-y: auto; 
            display: flex; 
            flex-direction: column; 
            gap: 12px;
            background: radial-gradient(circle at top, #252525 0%, #1e1e1e 100%);
        }
        #chat-window::-webkit-scrollbar { width: 6px; }
        #chat-window::-webkit-scrollbar-track { background: #1e1e1e; }
        #chat-window::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        #chat-window::-webkit-scrollbar-thumb:hover { background: #ffcc00; }
        .message { 
            padding: 12px 16px; 
            border-radius: 14px; 
            max-width: 85%; 
            word-wrap: break-word; 
            font-size: 15px;
            line-height: 1.4;
        }
        .user { 
            background-color: #2d2d2d; 
            color: #ffffff;
            align-self: flex-end; 
            border-bottom-right-radius: 2px;
            border: 1px solid #3d3d3d;
        }
        .bot { 
            background-color: #ffcc00; 
            color: #121212;
            align-self: flex-start; 
            border-bottom-left-radius: 2px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(255, 204, 0, 0.2);
        }
        .system-status {
            background-color: transparent !important;
            color: #888888 !important;
            border: 1px dashed #444;
            font-style: italic;
        }
        #input-area { 
            display: flex; 
            background: #121212;
            padding: 12px;
            gap: 10px;
            border-top: 1px solid #2d2d2d;
        }
        #user-input { 
            flex: 1; 
            padding: 14px 20px; 
            border: 1px solid #2d2d2d; 
            border-radius: 25px;
            background: #1e1e1e; 
            color: #fff; 
            outline: none; 
            font-size: 15px;
        }
        #user-input:focus { border-color: #ffcc00; }
        #send-btn { 
            width: 48px;
            height: 48px;
            background: #ffcc00; 
            border: none; 
            border-radius: 50%;
            color: #121212; 
            cursor: pointer; 
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #send-btn svg { width: 20px; height: 20px; fill: #121212; }
    </style>
</head>
<body>

    <h2>Верити // Онлайн</h2>
    
    <div id="chat-container">
        <div id="chat-window">
            <div class="message bot">Че надо, бездарь? Спрашивай свою глупость, я жду.</div>
        </div>
        <div id="input-area">
            <input type="text" id="user-input" placeholder="Напиши что-нибудь..." autocomplete="off">
            <button id="send-btn" title="Отправить">
                <svg viewBox="0 0 24 24">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                </svg>
            </button>
        </div>
    </div>

    <script>
        const chatWindow = document.getElementById('chat-window');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        function appendMessage(text, sender, isStatus = false) {
            const msgDiv = document.createElement('div');
            msgDiv.classList.add('message', sender);
            if (isStatus) msgDiv.classList.add('system-status');
            msgDiv.innerText = text;
            chatWindow.appendChild(msgDiv);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            return msgDiv;
        }

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            userInput.value = '';

            const typingDiv = appendMessage("Верити думает, как тебя разнести...", 'bot', true);

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                
                typingDiv.classList.remove('system-status');
                typingDiv.innerText = data.reply;
            } catch (error) {
                typingDiv.classList.remove('system-status');
                typingDiv.innerText = "я не знаю, но что то случится через 3 дня.";
            }
        }

        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    user_text = data.get('message', '')

    # Напрямую отправляем запрос к бесплатному серверу ИИ без капризных библиотек
    api_url = "https://huggingface.co"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{user_text}<|im_end|>\n<|im_start|>assistant\n"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100, "temperature": 0.8}
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        res_json = response.json()
        
        if isinstance(res_json, list) and "generated_text" in res_json[0]:
            full_text = res_json[0]["generated_text"]
            # Отрезаем промпт, оставляя только чистый ответ ИИ
            reply = full_text.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
        else:
            reply = "Че замолчал? Спроси нормально."
    except Exception:
        reply = "я не знаю, но что то случится через 3 дня."

    return jsonify({"reply": reply})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
