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

DB_PATH = 'redzone.db'

# ২. ডাটাবেস ও টেবিল তৈরি করার ফাংশন (এরর হ্যান্ডেলিং সহ)
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS videos 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           file_id TEXT, 
                           caption TEXT)''')
        conn.commit()
        conn.close()
        print("✅ Database & Table Initialized Successfully.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

# ৩. Flask রুট (Render-কে লাইভ রাখার জন্য)
@app.route('/')
def index():
    return "<h1>RedZone X is ONLINE</h1>", 200

@app.route('/api/videos')
def get_videos():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "file_id": r[1], "caption": r[2]} for r in rows])
    except Exception:
        return jsonify([])

# ৪. বটের কমান্ড (Welcome Message)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        web_app = types.WebAppInfo("https://rifatofficialsong1-cloud.github.io/RedZoneX/")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 Open RedZone X", web_app=web_app))
        
        bot.send_message(
            message.chat.id, 
            "🔥 *Welcome to RedZone X!*\n\nআপনার প্রিয় সব প্রিমিয়াম ভিডিও এখন টেলিগ্রাম মিনি অ্যাপে। নিচের বাটনে ক্লিক করে অ্যাপটি ওপেন করুন।", 
            parse_mode="Markdown", 
            reply_markup=markup
        )
    except Exception as e:
        print(f"Welcome Message Error: {e}")

# ভিডিও হ্যান্ডেলার
@bot.message_handler(content_types=['video'])
def handle_video(message):
    f_id = message.video.file_id
    cap = message.caption or "Premium Content"
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO videos (file_id, caption) VALUES (?, ?)", (f_id, cap))
        conn.commit()
        conn.close()
        bot.reply_to(message, "✅ ভিডিও সেভ হয়েছে! এখন এটি অ্যাপে দেখা যাবে।")
    except Exception as e:
        bot.reply_to(message, f"❌ Save Error: {str(e)}")

# ৫. রানার ফাংশন
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # ১. ডাটাবেস আগে তৈরি হবে
    init_db()
    
    # ২. ওয়েব সার্ভার ব্যাকগ্রাউন্ডে চলবে
    Thread(target=run_web, daemon=True).start()
    
    # ৩. ওয়েবহুক ক্লিয়ার করা
    print("Clearing webhooks and starting polling...")
    bot.remove_webhook()
    time.sleep(1)
    
    # ৪. ইনফিনিটি পোলিং (জোর করে চালু রাখা)
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=40)
        except Exception as e:
            print(f"Bot Polling Error: {e}")
            time.sleep(5)
