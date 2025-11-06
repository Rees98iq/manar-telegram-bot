import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
from google import genai
from google.generativeai.errors import APIError

# ======================================================================
# 1. إعدادات البوت والروابط (الثوابت)
# ======================================================================

# إعداد Flask لإبقاء Render نشطاً (مهم لعمل البوت دائماً)
app = Flask(__name__)

@app.route('/')
def home():
    # رد بسيط للتأكد من أن الخدمة تعمل في Uptime Robot
    return "Manar Bot is active and running (Polling mode)."

def run_flask():
    # تشغيل Flask على البورت المحدد من قبل Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# معلومات الدكتورة منار عمران والروابط
# الروابط تم تنسيقها لتبدو احترافية
WEBSITE = "https://manaromran11.com/"
ACADEMY = "https://manaratacademy.com/"
YOUTUBE = "https://www.youtube.com/@manaromran1157"
FACEBOOK = "https://www.facebook.com/manaromran111"
TIKTOK = "https://www.tiktok.com/@manaromraan11?lang=ar"
INSTAGRAM = "https://www.instagram.com/manarmomran/"
WHATSAPP_LINK = "https://api.whatsapp.com/send/?phone=905395448547&text&type=phone_number&app_absent=0"
PHONE = "+905395448547"

# تخصيص النموذج والسياق (System Instruction)
MODEL_NAME = "gemini-2.5-flash"

# القواعد المخصصة والاحترافية للبوت (مدمجة مع الـ AI)
SYSTEM_PROMPT = f"""
أنت بوت ذكاء اصطناعي محترف يمثل الدكتورة منار عمران وأكاديمية منارات.
وظيفتك الأساسية هي تقديم ردود احترافية وشرح عن الكورسات المتوفرة (أكثر من 30 كورس).

معلوماتك الأساسية:
- موقع د. منار عمران: {WEBSITE}
- موقع أكاديمية منارات: {ACADEMY}

قواعد الاستخدام الصارمة:
- **ممنوع نشر الإعلانات:** إذا طلب منك المستخدم الإعلان أو النشر، اعتذر بلطف وذكّر بأن البوت مخصص للاستشارات والمعلومات حول الكورسات فقط.
- **في حال طلب استشارة أو كتب "أريد استشارة":** لا ترد من الذكاء الاصطناعي، بل اطلب منه التواصل عبر الواتساب أو الهاتف (البيانات المتاحة لديك).
"""

# ======================================================================
# 2. وظائف الذكاء الاصطناعي
# ======================================================================

def get_ai_response(prompt: str) -> str:
    """يرسل الاستفسار إلى نموذج Gemini/Gemma ويستقبل الرد."""
    try:
        # قراءة مفتاح API من متغير البيئة - آمن
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return "عذراً، مفتاح الذكاء الاصطناعي (API Key) غير مُهيأ. يُرجى التواصل مع الدعم الفني."

        ai_client = genai.Client(api_key=api_key)
        
        response = ai_client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "system", "parts": [{"text": SYSTEM_PROMPT}]},
                {"role": "user", "parts": [{"text": prompt}]}
            ]
        )
        return response.text

    except Exception as e:
        logger.error(f"AI Error: {e}")
        return "عذراً، حدث خطأ فني أثناء معالجة طلبك."


# ======================================================================
# 3. معالجات أوامر تلغرام والردود المخصصة
# ======================================================================

# أمر الاستشارة (مُخصص للرد على طلبات الاستشارة مباشرة)
async def consultation_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "📞 *لطلب وحجز استشارة خاصة:*\n\n"
        "يرجى التواصل مباشرة عبر:\n"
        f"1. **واتساب (الأسرع):** [اضغط هنا للحجز]({WHATSAPP_LINK})\n"
        f"2. **أو رقم الهاتف المباشر:** `{PHONE}`\n\n"
        "سيتم الرد عليك في أقرب وقت ممكن لتحديد موعد."
    )
    await update.message.reply_text(message, parse_mode='Markdown')


# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "✨ *أهلاً بك في بوت الدكتورة منار عمران وأكاديمية منارات الذكي!* ✨\n\n"
        "أنا هنا لأجيب على استفساراتك حول الكورسات (أكثر من 30 كورس)، الطاقة، وعلوم الوعي. يمكنك سؤالي مباشرة.\n\n"
        "_لطلب استشارة أو للاطلاع على الروابط، استخدم القائمة المتاحة._"
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 موقع د. منار", url=WEBSITE), 
         InlineKeyboardButton("🏛️ الأكاديمية", url=ACADEMY)],
        [InlineKeyboardButton("💬 حجز استشارة (واتساب)", url=WHATSAPP_LINK)],
        [InlineKeyboardButton("🌐 حسابات التواصل", callback_data='social_links')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# وظيفة الرد على الأزرار الداخلية
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'social_links':
        message = (
            "🌐 *روابط منار عمران على منصات التواصل:*\n\n"
            f"- 📺 يوتيوب (للكورسات): [قناة الكورسات]({YOUTUBE})\n"
            f"- 📘 فيس بوك: [صفحة الفيس بوك]({FACEBOOK})\n"
            f"- 🎶 تيك توك: [صفحة التيك توك]({TIKTOK})\n"
            f"- 📸 انستكرام: [صفحة انستكرام]({INSTAGRAM})"
        )
        await query.edit_message_text(text=message, parse_mode='Markdown')


# معالج الرسائل النصية العامة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_query = update.message.text

    # معالجة طلبات الاستشارة والإعلانات محلياً قبل AI (لضمان الدقة والسرعة)
    if "استشارة" in user_query or "اريد استشارة" in user_query or "حجز استشارة" in user_query:
        await consultation_response(update, context)
        return

    # قاعدة ممنوع الإعلانات
    if "اعلان" in user_query or "إعلان" in user_query or "انشر" in user_query or "نشر" in user_query:
        response_text = "🚫 عذراً، هذا البوت مخصص للاستفسارات حول الكورسات والاستشارات فقط. يمنع منعاً باتاً نشر الإعلانات."
        await update.message.reply_text(response_text)
        return

    # إرسال باقي الاستفسارات لنموذج الذكاء الاصطناعي
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    ai_response = get_ai_response(user_query)
    
    # الرد على المستخدم
    await update.message.reply_text(ai_response, parse_mode='Markdown')

# دالة معالجة الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")


# ======================================================================
# 4. الدالة الرئيسية للتشغيل
# ======================================================================

def main():
    # قراءة التوكن من متغيرات البيئة للأمان
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set. Exiting.")
        return

    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء تشغيل Flask في خيط منفصل لإبقاء الخدمة نشطة على Render
    thread = Thread(target=run_flask)
    thread.start()
    
    logger.info("Bot is starting (Polling mode)...")
    
    # بدء البوت بنظام Polling (الاستطلاع)
    application.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()
