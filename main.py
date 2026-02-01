import os
import asyncio
from duckduckgo_search import DDGS
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Render အတွက် Web Server အသေးစားလေး လုပ်ထားတာပါ
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Bot Code ---
TOKEN = os.environ.get('TG_TOKEN') # Render Setting ထဲမှာ ထည့်ရမှာ

async def get_ai_response(user_input):
    try:
        with DDGS() as ddgs:
            prompt = f"You are a helpful Myanmar AI Bot. Answer in Burmese. User: {user_input}"
            results = ddgs.chat(prompt, model='gpt-4o-mini')
            return results
    except: return "ခဏလေးနော်၊ အလုပ်ရှုပ်နေလို့ပါ။"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        ai_reply = await get_ai_response(update.message.text)
        await update.message.reply_text(ai_reply)

if __name__ == '__main__':
    Thread(target=run_web).start() # Web server ကို နောက်ကွယ်မှာ run မယ်
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    bot_app.run_polling()
