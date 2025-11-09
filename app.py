from flask import Flask
import os
import telebot
import threading

TOKEN = "7767505553:AAE-doqqnURz2ySunKO5zgKMpwCwya92i70"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Бот запущен в хмарі! Тестую зв'язок...")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"📡 Отримав: {message.text}")

def run_bot():
    print("🚀 Запускаю Telegram бота...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Помилка бота: {e}")

@app.route('/')
def home():
    return "🎵 YouTube to MP3 Bot - Telegram Bot TEST"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    # Запускаємо бота в окремому потоці
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаємо Flask
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
