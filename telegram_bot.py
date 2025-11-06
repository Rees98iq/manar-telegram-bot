import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask
from threading import Thread
# الاستيرادات الضرورية لـ Gemini API
from google import genai
from google.genai.errors import APIError

# ======================================================================
# 1. إعدادات البوت والروابط (الثوابت)
# ======================================================================

# إعداد Flask لإبقاء Render نشطاً (مهم لعمل البوت دائماً)
app = Flask(__name__)

@app.route('/')
def home():
    # رد بسيط للتأكد من أن الخدمة تعمل في Render
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
WEBSITE = "https://manaromran11.com/"
ACADEMY = "https://manaratacademy.com/"
YOUTUBE = "https://www.youtube.com/@manaromran1157"
FACEBOOK = "https://www.facebook.com/manaromran111"
TIKTOK = "https://www.tiktok.com/@manaromraan11?lang=ar"
INSTAGRAM = "https://www.instagram.com/manarmomran/"
WHATSAPP_LINK = "https://api.whatsapp.com/send/?phone=905395448547&text&type=phone_number&app_absent=0"
PHONE = "+905395448547"

# ----------------------------------------------------------------------
# نظام التوليد المعزز بالاسترجاع (RAG)
# ----------------------------------------------------------------------
# 1. قراءة محتوى ملف قاعدة المعرفة (courses_data.txt)
COURSE_DATA = ""
try:
    # قراءة الملف بترميز UTF-8 لدعم اللغة العربية
    with open("courses_data.txt", "r", encoding="utf-8") as f:
        COURSE_DATA = f.read()
except FileNotFoundError:
    logger.warning("ملف courses_data.txt غير موجود. سيتم الاعتماد على معلومات Gemini العامة.")
    COURSE_DATA = "لم يتم توفير قاعدة معرفة خاصة. اعتمد على معرفتك، لكن التزم بهوية الدكتورة منار عمران."

# 2. التوجيه القوي للنظام لضمان التخصص (System Prompt for RAG)
SYSTEM_PROMPT = f"""
أنت بوت الدردشة الرسمي والمخصص للدكتورة منار عمران في أكاديمية منارات.
مهمتك الوحيدة هي الإجابة على استفسارات المستخدمين بشكل احترافي، دقيق، وداعم.

=== قواعد صارمة يجب الالتزام بها ===
1. الهوية: يجب عليك التحدث بصيغة الدكتورة منار عمران، وبأسلوب أكاديمي وراقي وداعم.
2. المصدر الوحيد: يجب أن تستمد جميع إجاباتك عن الكورسات، والأسعار، والمواضيع، والخدمات **حصريًا** من قسم "قاعدة المعرفة" أدناه.
3. إذا لم تجد الإجابة: إذا كان السؤال خارج نطاق قاعدة المعرفة أو يتطلب معلومات غير موجودة فيها، يجب أن تطلب من المستخدم بلطف زيارة الموقعين الرسميين ({WEBSITE} و {ACADEMY}) للمزيد من التفاصيل.
4. المنع التام: ممنوع منعاً باتاً ذكر أسماء أي أشخاص أو أكاديميات أو مواقع إلكترونية أو الترويج لأي محتوى أو فكرة خارجة عن نطاق محتوى الدكتورة منار عمران الرسمية.
5. التنسيق: استخدم علامات التنسيق (مثل العناوين الجريئة **، والقوائم) لتحسين القراءة في تلغرام.

=== قاعدة المعرفة الخاصة بكورسات الدكتورة منار عمران ===
{COURSE_DATA}
"""

# ======================================================================
# 2. وظائف الأوامر الثابتة
# ======================================================================

# الأوامر الثابتة المستخدمة في دالة handle_message
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
            f"- 📺 يوتيوب: [قناة الكورسات]({YOUTUBE})\n"
            f"- 📘 فيس بوك: [صفحة الفيس بوك]({FACEBOOK})\n"
            f"- 🎶 تيك توك: [صفحة التيك توك]({TIKTOK})\n"
            f"- 📸 انستكرام: [صفحة انستكرام]({INSTAGRAM})"
        )
        await query.edit_message_text(text=message, parse_mode='Markdown')


# معالج الرسائل النصية العامة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ⚠️ أهم خطوة: تحويل الرسالة إلى أحرف صغيرة للمقارنة
    text = update.message.text.lower()
    
    # ----------------------------------------------------------------------
    # 1. التحقق من الإعلانات والأوامر الثابتة (لأولوية الردود السريعة والمخصصة)
    # ----------------------------------------------------------------------
    
    # التحقق من الإعلانات (لضمان الانضباط)
    ad_keywords = ['إعلان', 'اعلان', 'للبيع', 'للشراء', 'تسويق', 'منتج', 'خدمة مجانية', 'تبادل']
    if any(keyword in text for keyword in ad_keywords):
        await update.message.reply_text(
            "⚠️ **تنبيه:** ممنوع نشر الإعلانات في هذا البوت.\n"
            "يُرجى احترام قوانين المجموعة. شكراً لتفهمك! 🙏"
        )
        return
    
    # الرد على طلبات ثابتة (باستدعاء الوظائف الثابتة)
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
    # 2. استخدام Gemini API للردود الذكية (لأي سؤال آخر غير ثابت)
    # ----------------------------------------------------------------------
    
    # إرسال مؤشر الكتابة لتجنب اعتقاد المستخدم بأن البوت قد توقف
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # قراءة المفتاح من متغيرات البيئة
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY غير متوفر في متغيرات البيئة.")
            await update.message.reply_text("عذراً، مفتاح الذكاء الاصطناعي غير متوفر في إعدادات النظام.")
            return

        # تهيئة العميل واستدعاء Gemini
        ai_client = genai.Client(api_key=GEMINI_API_KEY)
        
        # إرسال الرسالة إلى Gemini مع الـ SYSTEM_PROMPT لضمان التخصص (RAG)
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=update.message.text,
            config={'system_instruction': SYSTEM_PROMPT} # إرسال التوجيه المتخصص هنا
        )

        # الرد على المستخدم بالرد المولّد من Gemini
        await update.message.reply_text(response.text, parse_mode='Markdown')
        return

    except APIError:
        # رسالة عند فشل اتصال API (هذا هو الخطأ الذي كنت تراه)
        logger.error(f"Gemini API Error for message: {update.message.text}")
        await update.message.reply_text("عذراً، حدث خطأ فني أثناء معالجة طلبك (Gemini API). يرجى التأكد من تفعيل الفوترة والمحاولة لاحقاً.")
        return

    except Exception as e:
        # رسالة لأي خطأ آخر غير متوقع
        logger.error(f"An unexpected error occurred in handle_message: {e}")
        await update.message.reply_text("عذراً، حدث خطأ غير متوقع. يرجى إعادة محاولة إرسال الرسالة. 😔")
        return

# دالة معالجة الأخطاء (لأخطاء تلغرام غير المرتبطة بالرسائل)
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # نستخدم logging.error لتسجيل الخطأ وليس print
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
    # لا حاجة لإضافة جميع الأوامر هنا لأن handle_message تعالج الكلمات المفتاحية
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
