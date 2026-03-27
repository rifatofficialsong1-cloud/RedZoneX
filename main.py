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
    return "RedZone X Server is Active and Running!"

# অ্যাপের জন্য ভিডিও লিস্ট পাওয়ার API
@app.route('/api/videos')
def get_videos():
    try:
        conn = sqlite3.connect('redzone.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        videos = []
        for row in rows:
            videos.append({"id": row[0], "file_id": row[1], "caption": row[2]})
        return jsonify(videos)
    except Exception as e:
        return jsonify({"error": str(e)})

# /start কমান্ড দিলে ওয়েলকাম মেসেজ ও মিনি অ্যাপ বাটন
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup()
    # তোমার গিটহাব পেজ লিঙ্ক
    web_link = types.WebAppInfo("https://rifatofficialsong1-cloud.github.io/RedZoneX/")
    btn = types.InlineKeyboardButton("🚀 Open RedZone X", web_app=web_link)
    markup.add(btn)
    
    welcome_text = (
        "🔥 *Welcome to RedZone X!* 🔥\n\n"
        "আপনার প্রিয় সব প্রিমিয়াম ভিডিও এখন টেলিগ্রাম মিনি অ্যাপে।\n"
        "নিচের বাটনে ক্লিক করে অ্যাপটি ওপেন করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# ভিডিও সেভ করার কমান্ড
@bot.message_handler(content_types=['video'])
def save_video(message):
    file_id = message.video.file_id
    caption = message.caption or "Premium Video"
    
    try:
        conn = sqlite3.connect('redzone.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO videos (file_id, caption) VALUES (?, ?)", (file_id, caption))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ *ভিডিও সেভ হয়েছে!*\n\n📝 টাইটেল: {caption}\nএখন এটি মিনি অ্যাপে দেখা যাবে।", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ এরর: {str(e)}")

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    init_db()
    
    # ১. Flask সার্ভারকে ব্যাকগ্রাউন্ড থ্রেডে চালানো
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Forcefully clearing old connections...")
    bot.remove_webhook() # পুরনো কোনো ওয়েবহুক থাকলে তা মুছে দিবে
    
    print("RedZone X Bot is starting...")
    # ২. ইনফিনিটি পোলিং শুরু (পুরনো জমানো মেসেজ ইগনোর করে)
    bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
