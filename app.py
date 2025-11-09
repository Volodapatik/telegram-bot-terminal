from flask import Flask
import os
import subprocess
import threading

app = Flask(__name__)

# Запускаємо бота в окремому процесі
def start_bot_process():
    try:
        print("🚀 Starting Telegram bot in separate process...")
        subprocess.Popen(["python", "bot.py"])
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

@app.route('/')
def home():
    return "🎵 YouTube to MP3 Bot - Cloud Run Ready! Bot starting..."

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    # Запускаємо бота в окремому потоці
    bot_thread = threading.Thread(target=start_bot_process)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаємо Flask сервер
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
