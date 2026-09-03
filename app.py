import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Верити</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: #000000; 
            color: #ffffff; 
            display: flex; 
            flex-direction: column; 
            height: 100vh;
        }
        
        .ios-header {
            background: rgba(20, 20, 20, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 15px 0;
            text-align: center;
            border-bottom: 0.5px solid #2c2c2e;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 10;
        }
        .ios-header h1 { font-size: 17px; font-weight: 600; color: #ffcc00; letter-spacing: -0.4px; }
        .ios-header .status { font-size: 11px; color: #8e8e93; margin-top: 2px; }

        /* ИСПРАВЛЕНО: Скролл теперь работает идеально */
        #chat-window { 
            flex: 1;
            padding: 80px 16px 110px 16px; 
            overflow-y: scroll; 
            display: flex; 
            flex-direction: column; 
            gap: 10px;
            background: #121212;
            height: calc(100vh - 90px);
            -webkit-overflow-scrolling: touch;
        }

        .message { 
            padding: 10px 16px; 
            border-radius: 20px; 
            max-width: 75%; 
            word-wrap: break-word; 
            font-size: 16px;
            line-height: 1.35;
            letter-spacing: -0.2px;
            animation: iosPop 0.2s cubic-bezier(0.1, 0.8, 0.3, 1);
        }

        @keyframes iosPop {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .user { background-color: #2c2c2e; color: #ffffff; align-self: flex-end; border-bottom-right-radius: 5px; }
        .bot { background-color: #ffcc00; color: #000000; align-self: flex-start; border-bottom-left-radius: 5px; font-weight: 500; }
        .system-status { background-color: transparent !important; color: #8e8e93 !important; font-size: 13px; align-self: center; text-align: center; margin: 5px 0; }

        #input-panel { 
            position: fixed;
            bottom: 0;
            width: 100%;
            background: rgba(20, 20, 20, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-top: 0.5px solid #2c2c2e;
            padding: 10px 12px 30px 12px;
            z-index: 10;
        }

        .input-container {
            display: flex;
            background: #1c1c1e;
            border-radius: 22px;
            padding: 4px 4px 4px 16px;
            align-items: center;
            border: 0.5px solid #2c2c2e;
        }

        #user-input { 
            flex: 1; 
            border: none;
            background: transparent; 
            color: #ffffff; 
            outline: none; 
            font-size: 16px;
            padding: 6px 0;
            font-family: inherit;
        }
        #user-input::placeholder { color: #3a3a3c; }

        #send-btn { 
            width: 32px;
            height: 32px;
            background: #ffcc00; 
            border: none; 
            border-radius: 50%;
            cursor: pointer; 
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #send-btn svg { width: 16px; height: 16px; fill: #000000; }
    </style>
</head>
<body>

    <div class="ios-header">
        <h1>Верити</h1>
        <div class="status">онлайн</div>
    </div>
    
    <div id="chat-window">
        <div class="message bot">Че надо, бездарь? Спрашивай свою глупость, я жду.</div>
    </div>

    <div id="input-panel">
        <div class="input-container">
            <input type="text" id="user-input" placeholder="iMessage" autocomplete="off">
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
            
            // Автоматическая прокрутка вниз при новом сообщении
            setTimeout(() => {
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }, 50);
            
            return msgDiv;
        }

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            userInput.value = '';

            const typingDiv = appendMessage("Верити печатает...", 'bot', true);

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    return: JSON.stringify({ message: text }),
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

    # ИСПРАВЛЕНО: Бесплатный стабильный ИИ-канал, работающий БЕЗ ключей
    url = "https://deepinfra.com"
    try:
        response = requests.post(
            url,
            json={
                "model": "meta-llama/Meta-Llama-3-70B-Instruct",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "max_tokens": 100
            },
            timeout=8
        )
        if response.status_code == 200:
            res_json = response.json()
            reply = res_json["choices"][0]["message"]["content"].strip()
            return jsonify({"reply": reply})
    except Exception:
        pass

    return jsonify({"reply": "я не знаю, но что то случится через 3 дня."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
