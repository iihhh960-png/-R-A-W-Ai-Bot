import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# 1. Flask Web Server (Render Port စစ်တာ ကျော်ဖို့)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running properly!"

def run():
    # Render က ပေးတဲ့ Port ကို ယူသုံးမယ်၊ မရှိရင် 8080 သုံးမယ်
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Gemini AI & Telegram Bot Logic
TG_TOKEN = os.environ.get('TG_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        prompt = f"မင်းက မြန်မာလိုကျွမ်းကျင်တဲ့ AI Bot တစ်ခုပါ။ User ရဲ့စကားကို နားလည်ပြီး အလိုက်သင့်ယဉ်ကျေးစွာ ပြန်ဖြေပေးပါ။ User: {update.message.text}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == '__main__':
    # Web server ကို အရင်စဖွင့်မယ်
    keep_alive()
    
    # Telegram Bot ကို စဖွင့်မယ်
    bot_app = ApplicationBuilder().token(TG_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_handler))
    
    print("Bot is starting...")
    bot_app.run_polling()
