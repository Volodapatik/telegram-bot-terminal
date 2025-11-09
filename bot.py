import os
import telebot
import yt_dlp
import re
import subprocess
import sys

TOKEN = "7767505553:AAE-doqqnURz2ySunKO5zgKMpwCwya92i70"
bot = telebot.TeleBot(TOKEN)

# Переменная для контроля работы бота
bot_running = True
ADMIN_ID = 1637885523

def extract_url(text):
    match = re.search(r'youtu\.be/([^\s&]+)|youtube\.com/watch\?v=([^\s&]+)', text)
    return f"https://youtu.be/{match.group(1) or match.group(2)}" if match else None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎵 Бот запущен! Отправь ссылку YouTube\n\nДля остановки: /stop")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    """Остановка бота командой /stop"""
    global bot_running
    
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "🛑 Останавливаю бота...")
        print("Получена команда остановки от администратора")
        bot_running = False
        
        # Останавливаем polling
        bot.stop_polling()
        
        # Выходим из программы
        sys.exit(0)
    else:
        bot.reply_to(message, "❌ У вас нет прав для остановки бота")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    # Проверяем не остановлен ли бот
    if not bot_running:
        return
        
    url = extract_url(message.text)
    if not url:
        bot.reply_to(message, "❌ Неверная ссылка")
        return
    
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, f"🎵 Обрабатываю: {url}")
        
        # Скачиваем видео
        ydl_opts = {
            'format': 'worst[height<=360]',  # Самое простое видео
            'outtmpl': 'video.%(ext)s',
        }
        
        bot.send_message(chat_id, "⬇️ Скачиваю видео...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Проверяем что видео скачалось
        video_file = None
        for file in os.listdir('.'):
            if file.startswith('video.'):
                video_file = file
                break
        
        if not video_file:
            bot.reply_to(message, "❌ Не удалось скачать видео")
            return
        
        bot.send_message(chat_id, "🎵 Конвертирую в MP3...")
        
        # Конвертируем видео в MP3 с помощью FFmpeg
        mp3_file = 'audio.mp3'
        try:
            # Используем subprocess для вызова FFmpeg
            subprocess.run([
                'ffmpeg', '-i', video_file, 
                '-vn', '-acodec', 'libmp3lame', '-ab', '192k',
                '-y', mp3_file
            ], check=True, capture_output=True)
            
            # Проверяем что MP3 создался
            if os.path.exists(mp3_file):
                file_size = os.path.getsize(mp3_file) / (1024 * 1024)
                bot.send_message(chat_id, f"📤 Отправляю ({file_size:.1f} МБ)...")
                
                with open(mp3_file, 'rb') as f:
                    bot.send_audio(chat_id, f, timeout=300)
                
                bot.send_message(chat_id, "✅ Готово!")
                
                # Удаляем временные файлы
                os.remove(video_file)
                os.remove(mp3_file)
            else:
                bot.reply_to(message, "❌ Не удалось конвертировать в MP3")
                
        except subprocess.CalledProcessError as e:
            bot.reply_to(message, f"❌ Ошибка конвертации: {e}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

if __name__ == "__main__":
    print("🚀 Бот запущен с прямой конвертацией и остановкой!")
    print("💡 Для остановки отправьте /stop в боте")
    bot.infinity_polling()
