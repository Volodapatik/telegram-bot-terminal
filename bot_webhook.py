import os
import telebot
from flask import Flask

TOKEN = "7767505553:AAE-doqqnURz2ySunKO5zgKMpwCwya92i70"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎵 Бот запущен через вебхуки!")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    bot.reply_to(message, "🔄 Бот працює, але функціонал налаштовується...")

@app.route('/')
def home():
    return "🎵 YouTube to MP3 Bot - Webhook Ready!"

@app.route('/webhook/' + TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Error'

if __name__ == "__main__":
    # Видаляємо вебхук і встановлюємо новий
    bot.remove_webhook()
    bot.set_webhook(url=f"https://telegram-bot-terminal-228878747798.europe-west1.run.app/webhook/{TOKEN}")
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
