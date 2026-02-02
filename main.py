import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is Active", 200

# API Keys
TG_TOKEN = os.environ.get('TG_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# Gemini Configuration (Safety Filter များကို ပိတ်ခြင်း)
genai.configure(api_key=GEMINI_KEY)
# Safety setting များကို BLOCK_NONE ထားမှ စာပြန်မှာပါ
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        user_input = update.message.text
        response = model.generate_content(user_input)
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("AI က ဒီစကားလုံးကို အဖြေမထုတ်ပေးနိုင်ပါဘူး။")
            
    except Exception as e:
        print(f"Error: {e}")
        # Error တက်ရင် User သိအောင် ပြန်ပြောခိုင်းမယ်
        await update.message.reply_text(f"Error တက်သွားလို့ပါဗျာ။ အကြောင်းရင်းက: {str(e)[:50]}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    application = ApplicationBuilder().token(TG_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_reply))
    application.run_polling()

