import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Render အတွက် Web Server အသေးစား
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- API Keys (Render ရဲ့ Environment Variables ထဲမှာ ထည့်ရမှာ) ---
TG_TOKEN = os.environ.get('TG_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# Gemini AI Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # AI ကို စကားပြောခိုင်းခြင်း
        prompt = f"မင်းက မြန်မာလိုကျွမ်းကျင်တဲ့ AI Bot တစ်ခုပါ။ User ရဲ့စကားကို နားလည်ပြီး အလိုက်သင့်ယဉ်ကျေးစွာ ပြန်ဖြေပေးပါ။ User: {user_input}"
        response = model.generate_content(prompt)
        
        # User ကို Reply ပြန်ခြင်း
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("ခဏလေးနော်၊ အဖြေရှာရတာ ခက်ခဲနေလို့ပါ။")

if __name__ == '__main__':
    # Web server ကို နောက်ကွယ်မှာ run ထားမယ်
    Thread(target=run_web).start()
    
    # Bot ကို run မယ်
    bot_app = ApplicationBuilder().token(TG_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_handler))
    
    print("Gemini AI Bot is starting on Render...")
    bot_app.run_polling()
