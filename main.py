import os
import telebot
from flask import Flask, jsonify
from threading import Thread
import sqlite3
from telebot import types

# Render Environment Variable থেকে টোকেন নেওয়া
API_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ডাটাবেস সেটআপ
def init_db():
    conn = sqlite3.connect('redzone.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS videos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       file_id TEXT, 
                       caption TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return "RedZone X Server is Active!"

# অ্যাপের জন্য ভিডিও লিস্ট পাওয়ার API
@app.route('/api/videos')
def get_videos():
    try:
        conn = sqlite3.connect('redzone.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos")
        rows = cursor.fetchall()
        conn.close()
        
        videos = []
        for row in rows:
            videos.append({"id": row[0], "file_id": row[1], "caption": row[2]})
        return jsonify(videos)
    except Exception as e:
        return jsonify({"error": str(e)})

# /start কমান্ড দিলে ওয়েলকাম মেসেজ
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup()
    # আপনার গিটহাব পেজ লিঙ্কটি এখানে দিন
    web_link = types.WebAppInfo("https://rifatofficialsong1-cloud.github.io/RedZoneX/")
    btn = types.InlineKeyboardButton("🚀 Open RedZone X", web_app=web_link)
    markup.add(btn)
    
    welcome_text = (
        "🔥 *Welcome to RedZone X!* 🔥\n\n"
        "আপনার পছন্দের সব প্রিমিয়াম ভিডিও এখন এক জায়গায়। "
        "নিচের বাটনে ক্লিক করে আমাদের মিনি অ্যাপটি ওপেন করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ভিডিও সেভ করার কমান্ড (শুধুমাত্র আপনি ভিডিও পাঠালে সেভ হবে)
@bot.message_handler(content_types=['video'])
def save_video(message):
    file_id = message.video.file_id
    caption = message.caption or "Premium Video"
    
    conn = sqlite3.connect('redzone.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO videos (file_id, caption) VALUES (?, ?)", (file_id, caption))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, f"✅ *ভিডিও সাকসেসফুলি সেভ হয়েছে!*\n\n📝 ক্যাপশন: {caption}\nএখন এটি অ্যাপে দেখা যাবে।", parse_mode="Markdown")

def run_flask():
    # Render এর জন্য পোর্ট সেটআপ
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    init_db()
    # Flask কে আলাদা থ্রেডে চালানো
    Thread(target=run_flask, daemon=True).start()
    
    print("RedZone X Bot is starting...")
    # কোনো পুরনো ওয়েবহুক থাকলে মুছে ফেলা
    bot.remove_webhook()
    # বট পোলিং শুরু
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
