import os
import logging
import asyncio 
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# NEW: Import WsgiToAsgi to bridge Flask (WSGI) to Uvicorn (ASGI)
from asgiref.wsgi import WsgiToAsgi 
from flask import Flask, request, jsonify 
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from google import genai
from google.genai.errors import APIError

# ======================================================================
# 1. إعدادات البوت والروابط (الثوابت)
# ======================================================================

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# معلومات الدكتورة منار عمران والروابط
WEBSITE = "https://manaromran11.com/"
ACADEMY = "https://manaratacademy.com/"
YOUTUBE = "https://www.youtube.com/@manaromran1157"
FACEBOOK = "https://www.facebook.com/manaromran111"
TIKTOK = "https://www.tiktok.com/@manaromraan11?lang=ar"
INSTAGRAM = "https://www.instagram.com/manarmomran/"
WHATSAPP_LINK = "https://api.whatsapp.com/send/?phone=905395448547&text&type=phone_number&app_absent=0"
PHONE = "+905395448547"

# إعدادات الـ Webhook
PORT = int(os.environ.get('PORT', 10000))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_PATH = f"/{BOT_TOKEN}"
FULL_WEBHOOK_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

# ----------------------------------------------------------------------
# نظام التوليد المعزز بالاسترجاع (RAG)
# ----------------------------------------------------------------------
COURSE_DATA = ""
try:
    with open("courses_data.txt", "r", encoding="utf-8", errors='ignore') as f:
        COURSE_DATA = f.read()
except FileNotFoundError:
    logger.warning("ملف courses_data.txt غير موجود.")
    COURSE_DATA = "لم يتم توفير قاعدة معرفة خاصة. اعتمد على معرفتك، لكن التزم بهوية الدكتورة منار عمران."

SYSTEM_PROMPT = f"""
أنت بوت الدردشة الرسمي والمخصص للدكتورة منار عمران في أكاديمية منارات.
مهمتك الوحيدة هي الإجابة على استفسارات المستخدمين بشكل احترافي، دقيق، وداعم.

=== قواعد صارمة يجب الالتزام بها ===
1. الهوية: يجب عليك التحدث بصيغة الدكتورة منار عمران، وبأسلوب أكاديمي وراقي وداعم.
2. المصدر الوحيد: يجب أن تستمد جميع إجاباتك عن الكورسات، والأسعار، والمواضيع، والخدمات **حصريًا** من قسم "قاعدة المعرفة" أدناه.
3. إذا لم تجد الإجابة: إذا كان السؤال خارج نطاق قاعدة المعرفة أو يتطلب معلومات غير موجودة فيها، يجب أن تطلب من المستخدم بلطف زيارة الموقعين الرسميين ({WEBSITE} و {ACADEMY}) للمزيد من التفاصيل.
4. المنع التام: ممنوع منعاً باتاً ذكر أسماء أي أشخاص أو أكاديميات أو مواقع إلكترونية أو الترويج لأي محتوى أو فكرة خارجة عن نطاق محتوى الدكتورة منار عمران الرسمية.
5. **التنسيق: يجب أن يكون الرد نصًا عاديًا (Plain Text) فقط. ممنوع استخدام أي علامات تنسيق مثل Markdown أو HTML أو أي رموز خاصة (مثل *، **، _، #، [، ]).**

=== قاعدة المعرفة الخاصة بكورسات الدكتورة منار عمران ===
{COURSE_DATA}
"""

# ======================================================================
# 2. وظائف الأوامر الثابتة (باستخدام parse_mode='Markdown')
# ======================================================================

async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"📚 موقع الدكتورة منار عمران الرسمي:\n[اضغط هنا لزيارة الموقع]({WEBSITE})"
    await update.message.reply_text(message, parse_mode='Markdown')

async def academy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = f"🏛️ موقع أكاديمية منارات:\n[اضغط هنا لزيارة الأكاديمية]({ACADEMY})"
    await update.message.reply_text(message, parse_mode='Markdown')

async def courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "للاطلاع على الكورسات المتوفرة (أكثر من 30 كورس) والأسعار:\n"
    message += f"1. [موقع الأكاديمية]({ACADEMY})\n"
    message += f"2. [قناة اليوتيوب]({YOUTUBE})"
    await update.message.reply_text(message, parse_mode='Markdown')

async def consultation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "📞 *لطلب وحجز استشارة خاصة:*\n\n"
        "يرجى التواصل مباشرة عبر:\n"
        f"1. **واتساب (الأسرع):** [اضغط هنا للحجز]({WHATSAPP_LINK})\n"
        f"2. **أو رقم الهاتف المباشر:** `{PHONE}`\n\n"
        "سيتم الرد عليك في أقرب وقت ممكن لتحديد موعد."
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def social(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🌐 *روابط منار عمران على منصات التواصل:*\n\n"
        f"- 📺 يوتيوب: [قناة الكورسات]({YOUTUBE})\n"
        f"- 📘 فيس بوك: [صفحة الفيس بوك]({FACEBOOK})\n"
        f"- 🎶 تيك توك: [صفحة التيك توك]({TIKTOK})\n"
        f"- 📸 انستكرام: [صفحة انستكرام]({INSTAGRAM})"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

# ======================================================================
# 3. معالجات تلغرام الرئيسية (Start, Buttons, Message)
# ======================================================================

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'social_links':
        message = (
            "🌐 *روابط منار عمران على منصات التواصل:*\n\n"
            f"- 📺 يوتيوب: [قناة الكورسات]({YOUTUBE})\n"
            f"- 📘 فيس بوك: [صفحة الفيس بوك]({FACEBOOK})\n"
            f"- 🎶 تيك توك: [صفحة التيك توك]({TIKTOK})\n"
            f"- 📸 انستكرام: [صفحة انستكرام]({INSTAGRAM})"
        )
        await query.edit_message_text(text=message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    
    # ----------------------------------------------------------------------
    # 1. التحقق من الإعلانات والأوامر الثابتة
    # ----------------------------------------------------------------------
    
    ad_keywords = ['إعلان', 'اعلان', 'للبيع', 'للشراء', 'تسويق', 'منتج', 'خدمة مجانية', 'تبادل']
    if any(keyword in text for keyword in ad_keywords):
        await update.message.reply_text(
            "⚠️ **تنبيه:** ممنوع نشر الإعلانات في هذا البوت.\n"
            "يُرجى احترام قوانين المجموعة. شكراً لتفهمك! 🙏", parse_mode='Markdown'
        )
        return
    
    if any(word in text for word in ['موقع', 'الموقع', 'موقعك', 'website']):
        await website(update, context)
        return
    
    if any(word in text for word in ['أكاديمية', 'اكاديمية', 'academy']):
        await academy(update, context)
        return
    
    if any(word in text for word in ['كورس', 'كورسات', 'دورة', 'دورات', 'courses']):
        await courses(update, context)
        return
    
    if any(word in text for word in ['استشارة', 'استشاره', 'consultation', 'حجز استشارة', 'اريد استشارة']):
        await consultation(update, context)
        return
    
    if any(word in text for word in ['تواصل', 'حسابات', 'سوشيال', 'فيس', 'انستا', 'يوتيوب', 'تيك توك']):
        await social(update, context)
        return
    
    # ----------------------------------------------------------------------
    # 2. استخدام Gemini API للردود الذكية
    # ----------------------------------------------------------------------
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY غير متوفر.")
            await update.message.reply_text("عذراً، مفتاح الذكاء الاصطناعي غير متوفر في إعدادات النظام.")
            return

        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=update.message.text,
            config={'system_instruction': SYSTEM_PROMPT}
        )

        await update.message.reply_text(response.text) 
        return

    except APIError as api_e:
        logger.error(f"Gemini API Error: {api_e}")
        await update.message.reply_text("عذراً، حدث خطأ فني أثناء معالجة طلبك (Gemini API).")
        return

    except Exception as e:
        logger.error(f"An unexpected error occurred in handle_message: {e}")
        await update.message.reply_text("عذراً، حدث خطأ غير متوقع. يرجى إعادة محاولة إرسال الرسالة. 😔")
        return

def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")


# ======================================================================
# 4. الدالة الرئيسية للتشغيل (Webhook)
# ======================================================================

# 1. إعداد Flask (تطبيق WSGI الأصلي)
wsgi_app = Flask(__name__) # <<< متغير جديد للتطبيق الأصلي

# 2. إعداد Telegram Application
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_error_handler(error_handler)

# -----------------
# مسارات Flask (تستخدم wsgi_app)
# -----------------

@wsgi_app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook_handler():
    """معالج طلبات تلغرام الواردة."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    
    return jsonify({"status": "ok"}), 200

@wsgi_app.route('/', methods=['GET'])
def health_check():
    """مسار اختبار صحة الخدمة لـ Render"""
    return "Bot is running via Webhook!", 200

# -----------------
# 3. التطبيق النهائي المكشوف لـ Gunicorn/Uvicorn
# -----------------
# يتم تغليف تطبيق Flask (wsgi_app) باستخدام WsgiToAsgi
# ويتم تعيينه للمتغير 'app' الذي تبحث عنه Gunicorn.
app = WsgiToAsgi(wsgi_app) 


# -----------------
# 4. دالة الإطلاق والتحقق من الـ Webhook
# -----------------

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN غير متوفر. يتم الإغلاق.")
        return
        
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL غير متوفر. يجب إعداده. يتم الإغلاق.")
        return

    # إعداد الـ Webhook (يتم تنفيذه مرة واحدة عبر 'python telegram_bot.py' في مرحلة النشر)
    try:
        logger.info(f"Setting webhook to: {FULL_WEBHOOK_URL}")
        asyncio.run(application.bot.set_webhook(url=FULL_WEBHOOK_URL))
        logger.info("Webhook set successfully.")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return


if __name__ == '__main__':
    main()
