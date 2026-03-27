import os
import telebot
from flask import Flask, jsonify
from threading import Thread
import sqlite3

# টোকেন সরাসরি কোডে না রেখে Environment Variable থেকে নেওয়া হচ্ছে
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
    return "RedZone X Server is Running!"

# অ্যাপের জন্য ভিডিও লিস্ট পাওয়ার API
@app.route('/api/videos')
def get_videos():
    conn = sqlite3.connect('redzone.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos")
    rows = cursor.fetchall()
    conn.close()
    
    videos = []
    for row in rows:
        videos.append({"id": row[0], "file_id": row[1], "caption": row[2]})
    return jsonify(videos)

# ভিডিও সেভ করার কমান্ড
@bot.message_handler(content_types=['video'])
def save_video(message):
    file_id = message.video.file_id
    caption = message.caption or "New Video"
    
    conn = sqlite3.connect('redzone.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO videos (file_id, caption) VALUES (?, ?)", (file_id, caption))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, f"✅ ভিডিও সেভ হয়েছে!\nCaption: {caption}")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    init_db()
    Thread(target=run_flask).start()
    print("Bot & Server Started...")
    bot.infinity_polling()
