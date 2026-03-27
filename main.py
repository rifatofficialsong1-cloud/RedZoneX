import os
import telebot
import time
import sqlite3
from flask import Flask, jsonify
from threading import Thread
from telebot import types

# ১. সেটিংস ও টোকেন
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ২. ডাটাবেস ইনিশিয়ালাইজেশন
def init_db():
    conn = sqlite3.connect('redzone.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       file_id TEXT, 
                       caption TEXT)''')
    conn.commit()
    conn.close()

# ৩. Render-কে খুশি রাখার জন্য রুট (নাহলে Render সার্ভিস বন্ধ করে দেয়)
@app.route('/')
def index():
    return "<h1>RedZone X is ONLINE</h1>", 200

@app.route('/api/videos')
def get_videos():
    conn = sqlite3.connect('redzone.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "file_id": r[1], "caption": r[2]} for r in rows])

# ৪. বটের কমান্ড ও ভিডিও সেভ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    web_app = types.WebAppInfo("https://rifatofficialsong1-cloud.github.io/RedZoneX/")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🚀 Open RedZone X", web_app=web_app))
    bot.reply_to(message, "🔥 *Welcome to RedZone X!*\nনিচের বাটনে ক্লিক করে মিনি অ্যাপ ওপেন করুন।", 
                 parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    f_id = message.video.file_id
    cap = message.caption or "Premium Content"
    conn = sqlite3.connect('redzone.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO videos (file_id, caption) VALUES (?, ?)", (f_id, cap))
    conn.commit()
    conn.close()
    bot.reply_to(message, "✅ ভিডিও সেভ হয়েছে!")

# ৫. মেইন রানার (Flask + Bot)
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    init_db()
    # ওয়েব সার্ভার আলাদা থ্রেডে চালু
    Thread(target=run_web, daemon=True).start()
    
    print("Starting Bot Polling...")
    bot.remove_webhook()
    
    # ৬. ইনফিনিটি লুপ যাতে বট কখনো না মরে
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
