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
<html lang="ru" data-theme="ios">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Верити</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; transition: background 0.3s, color 0.3s, border-color 0.3s; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: #000000; 
            color: #ffffff; 
            display: flex; 
            flex-direction: column; 
            height: 100vh;
            overflow: hidden;
        }
        
        /* Кнопка переключения дизайна в шапке */
        .theme-btn {
            position: absolute;
            right: 16px;
            top: 12px;
            background: rgba(255, 204, 0, 0.2);
            border: 1px solid #ffcc00;
            color: #ffcc00;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
        }

        /* --- 1. iOS СТИЛЬ (ПО УМОЛЧАНИЮ) --- */
        html[data-theme="ios"] body { background: #000; font-family: -apple-system, sans-serif; }
        html[data-theme="ios"] .ios-header { background: rgba(20, 20, 20, 0.75); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 15px 0; text-align: center; border-bottom: 0.5px solid #2c2c2e; position: fixed; top: 0; width: 100%; z-index: 10; }
        html[data-theme="ios"] .ios-header h1 { font-size: 17px; font-weight: 600; color: #ffcc00; }
        html[data-theme="ios"] #chat-window { background: #121212; padding: 80px 16px 110px 16px; }
        html[data-theme="ios"] .message { border-radius: 20px; font-size: 16px; }
        html[data-theme="ios"] .user { background-color: #2c2c2e; color: #fff; align-self: flex-end; border-bottom-right-radius: 5px; }
        html[data-theme="ios"] .bot { background-color: #ffcc00; color: #000; align-self: flex-start; border-bottom-left-radius: 5px; font-weight: 500; }
        html[data-theme="ios"] #input-panel { position: fixed; bottom: 0; width: 100%; background: rgba(20, 20, 20, 0.85); backdrop-filter: blur(20px); border-top: 0.5px solid #2c2c2e; padding: 10px 12px 30px 12px; }
        html[data-theme="ios"] .input-container { display: flex; background: #1c1c1e; border-radius: 22px; padding: 4px 4px 4px 16px; border: 0.5px solid #2c2c2e; }
        html[data-theme="ios"] #user-input { flex: 1; border: none; background: transparent; color: #fff; font-size: 16px; }
        html[data-theme="ios"] #send-btn { width: 32px; height: 32px; background: #ffcc00; border: none; border-radius: 50%; }

        /* --- 2. СТАРЫЙ СТИЛЬ (CYBERPUNK) --- */
        html[data-theme="cyberpunk"] body { background: #121212; font-family: 'Segoe UI', Arial, sans-serif; }
        html[data-theme="cyberpunk"] .ios-header { background: #1e1e1e; padding: 15px 0; border-bottom: 1px solid #2d2d2d; position: fixed; top: 0; width: 100%; text-align: center; }
        html[data-theme="cyberpunk"] .ios-header h1 { color: #ffcc00; font-size: 20px; text-transform: uppercase; letter-spacing: 2px; }
        html[data-theme="cyberpunk"] #chat-window { background: radial-gradient(circle at top, #252525 0%, #1e1e1e 100%); padding: 80px 16px 110px 16px; }
        html[data-theme="cyberpunk"] .message { border-radius: 14px; font-size: 15px; }
        html[data-theme="cyberpunk"] .user { background: #2d2d2d; color: #fff; align-self: flex-end; border: 1px solid #3d3d3d; border-bottom-right-radius: 2px; }
        html[data-theme="cyberpunk"] .bot { background: #ffcc00; color: #121212; align-self: flex-start; border-bottom-left-radius: 2px; font-weight: 600; }
        html[data-theme="cyberpunk"] #input-panel { position: fixed; bottom: 0; width: 100%; background: #121212; padding: 15px 12px; border-top: 1px solid #2d2d2d; }
        html[data-theme="cyberpunk"] .input-container { display: flex; background: #1e1e1e; border-radius: 25px; padding: 6px 6px 6px 16px; border: 1px solid #2d2d2d; }
        html[data-theme="cyberpunk"] #user-input { flex: 1; border: none; background: transparent; color: #fff; }
        html[data-theme="cyberpunk"] #send-btn { width: 36px; height: 36px; background: #ffcc00; border-radius: 50%; }

        /* --- 3. MICROSOFT СТИЛЬ (FLUENT) --- */
        html[data-theme="microsoft"] body { background: #0b0f19; font-family: "Segoe UI", system-ui, sans-serif; }
        html[data-theme="microsoft"] .ios-header { background: rgba(15, 23, 42, 0.8); border-bottom: 1px solid rgba(255,255,255,0.1); padding: 15px 0; position: fixed; top: 0; width: 100%; text-align: center; }
        html[data-theme="microsoft"] .ios-header h1 { color: #ffffff; font-size: 18px; font-weight: 400; }
        html[data-theme="microsoft"] #chat-window { background: #0f172a; padding: 80px 16px 110px 16px; }
        html[data-theme="microsoft"] .message { border-radius: 8px; font-size: 15px; border: 1px solid rgba(255,255,255,0.05); }
        html[data-theme="microsoft"] .user { background: #1e293b; color: #fff; align-self: flex-end; }
        html[data-theme="microsoft"] .bot { background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%); color: #000; align-self: flex-start; font-weight: 500; box-shadow: 0 4px 12px rgba(255,170,0,0.15); }
        html[data-theme="microsoft"] #input-panel { position: fixed; bottom: 0; width: 100%; background: #0f172a; padding: 15px 16px 35px 16px; border-top: 1px solid rgba(255,255,255,0.05); }
        html[data-theme="microsoft"] .input-container { display: flex; background: #1e293b; border-radius: 8px; padding: 6px 8px; border: 1px solid rgba(255,255,255,0.1); }
        html[data-theme="microsoft"] #user-input { flex: 1; border: none; background: transparent; color: #fff; }
        html[data-theme="microsoft"] #send-btn { width: 34px; height: 34px; background: #ffaa00; border-radius: 4px; }

        /* Общие неизменяемые стили скролла */
        #chat-window { 
            flex: 1;
            overflow-y: scroll; 
            display: flex; 
            flex-direction: column; 
            gap: 10px;
            height: calc(100vh - 90px);
            -webkit-overflow-scrolling: touch;
        }
        #chat-window::-webkit-scrollbar { width: 4px; }
        #chat-window::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }

        .system-status { background-color: transparent !important; color: #8e8e93 !important; font-size: 13px; align-self: center; text-align: center; margin: 5px 0; border: none !important; box-shadow: none !important; }
    </style>
</head>
<body>

    <div class="ios-header">
        <h1 id="header-title">Верити</h1>
        <div class="theme-btn" onclick="toggleTheme()">Дизайн</div>
    </div>
    
    <div id="chat-window">
        <div class="message bot">Че надо, бездарь? Спрашивай свою глупость, я жду.</div>
    </div>

    <div id="input-panel">
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Напиши что-нибудь..." autocomplete="off">
            <button id="send-btn" title="Отправить">
                <svg viewBox="0 0 24 24" style="width:16px; height:16px; fill:currentColor;">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                </svg>
            </button>
        </div>
    </div>

    <script>
        const chatWindow = document.getElementById('chat-window');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const themes = ['ios', 'cyberpunk', 'microsoft'];
        let currentThemeIndex = 0;

        function toggleTheme() {
            currentThemeIndex = (currentThemeIndex + 1) % themes.length;
            const newTheme = themes[currentThemeIndex];
            document.documentElement.setAttribute('data-theme', newTheme);
            
            const title = document.getElementById('header-title');
            if(newTheme === 'ios') title.innerText = "Верити // iOS";
            if(newTheme === 'cyberpunk') title.innerText = "Верити // СТАРЫЙ";
            if(newTheme === 'microsoft') title.innerText = "Верити // MICROSOFT";
        }

        function appendMessage(text, sender, isStatus = false) {
            const msgDiv = document.createElement('div');
            msgDiv.classList.add('message', sender);
            if (isStatus) msgDiv.classList.add('system-status');
            msgDiv.innerText = text;
            chatWindow.appendChild(msgDiv);
            
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

            const typingDiv = appendMessage("Верити придумывает ответ...", 'bot', true);

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                
typingDiv.classList.remove('system-status');typingDiv.innerText = data.reply;} catch (error) {typingDiv.classList.remove('system-status');typingDiv.innerText = "я не знаю, но что то случится через 3 дня.";}}sendBtn.addEventListener('click', sendMessage);userInput.addEventListener('keypress', (e) => {if (e.key === 'Enter') sendMessage();});"""@app.route('/')def home():return render_template_string(HTML_TEMPLATE)@app.route('/ask', methods=['POST'])def ask():data = request.get_json() or {}user_text = data.get('message', '')# ПРЯМОЙ И СТАБИЛЬНЫЙ ВЫЗОВ ЧЕРЕЗ БЕСПЛАТНЫЙ ШЛЮЗ DUCKDUCKGO AI (БЕЗ КЛЮЧЕЙ)url = "duckduckgo.com"headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","Accept": "text/event-stream","x-vqd-4": "1"}try:# Шаг 1: Получаем внутренний токен сессии (vqd)init_res = requests.get("duckduckgo.com", headers={"x-vqd-4": "1"})vqd = init_res.headers.get("x-vqd-4")if vqd:headers["x-vqd-4"] = vqd# Шаг 2: Отправляем запрос модели Llama-3res = requests.post(url,headers=headers,json={"model": "meta-llama/Meta-Llama-3-70B-Instruct","messages": [{"role": "system", "content": SYSTEM_PROMPT},{"role": "user", "content": user_text}]},timeout=8)if res.status_code == 200:# Обработка потокового ответа от DDGfull_reply = ""for line in res.text.split("\n"):if line.startswith("data: "):data_str = line[6:].strip()if data_str == "[DONE]":breaktry:import jsonchunk = json.loads(data_str)if "message" in chunk:full_reply += chunk["message"]except:passif full_reply:return jsonify({"reply": full_reply.strip()})except:passreturn jsonify({"reply": "я не знаю, но что то случится через 3 дня."})if name == 'main':port = int(os.environ.get("PORT", 5000))app.run(host='0.0.0.0', port=port)
