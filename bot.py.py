import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Flask app بسيط لإبقاء Render نشطاً
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# معلومات الدكتورة منار عمران
WEBSITE = "https://manaromran11.com/"
ACADEMY = "https://manaratacademy.com/"
YOUTUBE = "https://www.youtube.com/@manaromran1157"
FACEBOOK = "https://www.facebook.com/manaromran111"
TIKTOK = "https://www.tiktok.com/@manaromraan11?lang=ar"
INSTAGRAM = "https://www.instagram.com/manarmomran/"
WHATSAPP = "https://api.whatsapp.com/send/?phone=905395448547&text&type=phone_number&app_absent=0"
PHONE = "+905395448547"

# أمر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إنشاء لوحة مفاتيح تفاعلية
    keyboard = [
        [InlineKeyboardButton("📚 الكورسات", callback_data='courses'),
         InlineKeyboardButton("🌐 الموقع", callback_data='website')],
        [InlineKeyboardButton("🎓 الأكاديمية", callback_data='academy'),
         InlineKeyboardButton("💼 حجز استشارة", callback_data='consultation')],
        [InlineKeyboardButton("📱 التواصل الاجتماعي", callback_data='social'),
         InlineKeyboardButton("❓ المساعدة", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = """
🌟 مرحباً بك في بوت الدكتورة منار عمران 🌟

أهلاً وسهلاً! يسعدني مساعدتك في الوصول إلى كل ما تحتاجه من:

📚 **الكورسات التعليمية** (أكثر من 30 كورس)
🎓 **الأكاديمية والبرامج التدريبية**
💡 **الاستشارات الشخصية والمهنية**
🌐 **روابط التواصل الاجتماعي**

استخدم الأزرار أدناه للوصول السريع، أو اكتب ما تبحث عنه! 😊

⚠️ **تنبيه مهم:** ممنوع نشر الإعلانات في هذا البوت
"""
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# أمر المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **قائمة الأوامر المتاحة:**

/start - رسالة الترحيب
/courses - عرض الكورسات المتاحة
/website - رابط الموقع الإلكتروني
/academy - رابط الأكاديمية
/social - روابط التواصل الاجتماعي
/consultation - حجز استشارة
/help - عرض هذه الرسالة

يمكنك أيضاً كتابة أي استفسار وسأساعدك! 💫
"""
    await update.message.reply_text(help_text)

# أمر الكورسات
async def courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    courses_message = f"""
📚 **الكورسات التعليمية للدكتورة منار عمران**

نقدم لك أكثر من **30 كورس تعليمي** متخصص يغطي مجالات متنوعة!

🎓 **أمثلة من الكورسات المتاحة:**
• كورس الخوف وعلاجاته 🧠
• التطوير الشخصي والنمو الذاتي ✨
• المهارات الاحترافية والقيادية 💼
• التسويق الرقمي والإلكتروني 📱
• العلاقات الإنسانية والاجتماعية 🤝
• الصحة النفسية والعاطفية 💚
• مهارات التواصل الفعّال 🗣️
• إدارة الوقت والإنتاجية ⏰
• الذكاء العاطفي والاجتماعي 🌟
• وأكثر من 20 كورس آخر!

🌐 **حيث تجد الكورسات:**

**1️⃣ موقع الدكتورة منار عمران:**
{WEBSITE}
✅ كورسات شاملة ومتنوعة
✅ محتوى احترافي ومنظم
✅ شهادات معتمدة عند الانتهاء
✅ تعلم بالسرعة التي تناسبك

**2️⃣ أكاديمية منار:**
{ACADEMY}
✅ برامج تدريبية متقدمة
✅ مسارات تعليمية متكاملة
✅ متابعة ودعم مستمر
✅ تدريب عملي وتطبيقي

**3️⃣ قناة اليوتيوب:**
{YOUTUBE}
✅ كورسات مجانية
✅ محتوى تعليمي قيّم
✅ فيديوهات تحفيزية
✅ تحديثات أسبوعية

🎯 **لماذا تختار كورساتنا؟**
• خبرة طويلة في المجال
• محتوى عربي أصيل وعالي الجودة
• دعم فني ومتابعة مستمرة
• أسعار تنافسية ومناسبة
• إمكانية الوصول مدى الحياة

📈 **ابدأ رحلتك التعليمية الآن واستثمر في نفسك!**
"""
    await update.message.reply_text(courses_message)

# أمر الموقع
async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    website_message = f"""
🌐 **موقع الدكتورة منار عمران الإلكتروني**

{WEBSITE}

الموقع يقدم لك:
✨ أكثر من 30 كورس تعليمي متخصص
✨ محتوى تعليمي احترافي ومنظم
✨ شهادات معتمدة
✨ إمكانية التعلم الذاتي بالوقت المناسب لك
✨ دعم ومتابعة مستمرة

زر الموقع الآن واستكشف كل ما هو جديد! 🎯
"""
    await update.message.reply_text(website_message)

# أمر الأكاديمية
async def academy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    academy_message = f"""
🎓 **أكاديمية منار للتدريب**

{ACADEMY}

الأكاديمية توفر لك:
🌟 برامج تدريبية متقدمة
🌟 مسارات تعليمية متكاملة
🌟 كورسات متخصصة في مجالات متنوعة
🌟 شهادات احترافية معتمدة
🌟 متابعة فردية ودعم مستمر

انضم لآلاف المتدربين واصنع مستقبلك المهني! 💼
"""
    await update.message.reply_text(academy_message)

# أمر التواصل الاجتماعي
async def social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    social_message = f"""
📱 **تابعنا على وسائل التواصل الاجتماعي**

تواصل مع الدكتورة منار عمران على جميع المنصات:

📺 **يوتيوب:**
{YOUTUBE}

👥 **فيسبوك:**
{FACEBOOK}

🎵 **تيك توك:**
{TIKTOK}

📸 **انستغرام:**
{INSTAGRAM}

تابعنا للحصول على:
• محتوى تعليمي يومي
• نصائح وإرشادات مفيدة
• إعلانات الكورسات الجديدة
• تحديثات حصرية

نحن في انتظارك! 💫
"""
    await update.message.reply_text(social_message)

# أمر الاستشارة
async def consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    consultation_message = f"""
💼 **حجز استشارة مع الدكتورة منار عمران**

هل تحتاج إلى استشارة شخصية أو مهنية؟
الدكتورة منار جاهزة لمساعدتك! 🌟

📞 **طرق التواصل لحجز الاستشارة:**

**1️⃣ واتساب (الطريقة الأسرع):**
{WHATSAPP}

**2️⃣ الاتصال المباشر:**
{PHONE}

🎯 **ما ستحصل عليه:**
• استشارة شخصية ومخصصة
• حلول عملية لمشاكلك
• توجيه احترافي
• خطة عمل واضحة

لا تتردد في التواصل الآن! ⏰
"""
    await update.message.reply_text(consultation_message)

# معالج الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # التحقق من الإعلانات
    ad_keywords = ['إعلان', 'اعلان', 'للبيع', 'للشراء', 'تسويق', 'منتج', 'خدمة مجانية']
    if any(keyword in text for keyword in ad_keywords):
        await update.message.reply_text(
            "⚠️ **تنبيه:** ممنوع نشر الإعلانات في هذا البوت.\n"
            "يُرجى احترام قوانين المجموعة. شكراً لتفهمك! 🙏"
        )
        return
    
    # الرد على طلبات الموقع
    if any(word in text for word in ['موقع', 'الموقع', 'موقعك', 'website']):
        await website(update, context)
        return
    
    # الرد على طلبات الأكاديمية
    if any(word in text for word in ['أكاديمية', 'اكاديمية', 'academy']):
        await academy(update, context)
        return
    
    # الرد على طلبات الكورسات
    if any(word in text for word in ['كورس', 'كورسات', 'دورة', 'دورات', 'courses']):
        await courses(update, context)
        return
    
    # الرد على طلبات الاستشارة
    if any(word in text for word in ['استشارة', 'استشاره', 'consultation', 'استفسار', 'سؤال']):
        await consultation(update, context)
        return
    
    # الرد على طلبات التواصل
    if any(word in text for word in ['تواصل', 'حسابات', 'سوشيال', 'فيس', 'انستا', 'يوتيوب', 'تيك توك']):
        await social(update, context)
        return
    
    # رد عام
    await update.message.reply_text(
        "شكراً لرسالتك! 😊\n\n"
        "يمكنك استخدام الأوامر التالية:\n"
        "• /courses للكورسات\n"
        "• /website للموقع\n"
        "• /consultation للاستشارة\n"
        "• /help للمساعدة\n\n"
        "أو اكتب ما تبحث عنه وسأساعدك! 💫"
    )

# معالج الأزرار التفاعلية
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # إنشاء لوحة المفاتيح للعودة
    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query.data == 'start':
        # إعادة عرض القائمة الرئيسية
        keyboard = [
            [InlineKeyboardButton("📚 الكورسات", callback_data='courses'),
             InlineKeyboardButton("🌐 الموقع", callback_data='website')],
            [InlineKeyboardButton("🎓 الأكاديمية", callback_data='academy'),
             InlineKeyboardButton("💼 حجز استشارة", callback_data='consultation')],
            [InlineKeyboardButton("📱 التواصل الاجتماعي", callback_data='social'),
             InlineKeyboardButton("❓ المساعدة", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🌟 **القائمة الرئيسية**\n\nاختر ما تحتاجه من الأزرار أدناه:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif query.data == 'courses':
        message = f"""
📚 **الكورسات التعليمية للدكتورة منار عمران**

نقدم لك أكثر من **30 كورس تعليمي** متخصص!

🎓 **أمثلة من الكورسات:**
• كورس الخوف وعلاجاته 🧠
• التطوير الشخصي ✨
• المهارات القيادية 💼
• التسويق الرقمي 📱
• العلاقات الإنسانية 🤝
• الصحة النفسية 💚

🌐 **المواقع:**
• الموقع: {WEBSITE}
• الأكاديمية: {ACADEMY}
• يوتيوب: {YOUTUBE}
"""
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == 'website':
        message = f"""
🌐 **موقع الدكتورة منار عمران**

{WEBSITE}

✨ أكثر من 30 كورس تعليمي
✨ محتوى احترافي ومنظم
✨ شهادات معتمدة
✨ دعم ومتابعة مستمرة
"""
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == 'academy':
        message = f"""
🎓 **أكاديمية منار**

{ACADEMY}

🌟 برامج تدريبية متقدمة
🌟 مسارات تعليمية متكاملة
🌟 شهادات احترافية
🌟 متابعة فردية
"""
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == 'consultation':
        message = f"""
💼 **حجز استشارة**

📞 **واتساب:**
{WHATSAPP}

📱 **هاتف:**
{PHONE}

🎯 استشارة مخصصة لك!
"""
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == 'social':
        message = f"""
📱 **تابعنا على:**

📺 يوتيوب: {YOUTUBE}
👥 فيسبوك: {FACEBOOK}
🎵 تيك توك: {TIKTOK}
📸 انستغرام: {INSTAGRAM}
"""
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif query.data == 'help':
        message = """
📖 **المساعدة**

**الأوامر:**
/start - البداية
/courses - الكورسات
/website - الموقع
/academy - الأكاديمية
/consultation - حجز استشارة
/social - التواصل
/help - المساعدة

أو اكتب ما تبحث عنه! 💫
"""
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# دالة معالجة الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

# الدالة الرئيسية
def main():
    # إنشاء التطبيق
    # يمكنك استخدام متغير بيئة للتوكن للأمان
    # BOT_TOKEN = os.getenv('BOT_TOKEN', '8265161343:AAFgiWyxz-BSZN1MA1iu-qYdLYzlapgCJzo')
    application = Application.builder().token("8265161343:AAFgiWyxz-BSZN1MA1iu-qYdLYzlapgCJzo").build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("courses", courses))
    application.add_handler(CommandHandler("website", website))
    application.add_handler(CommandHandler("academy", academy))
    application.add_handler(CommandHandler("social", social))
    application.add_handler(CommandHandler("consultation", consultation))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # إضافة معالج الأخطاء
    application.add_error_handler(error_handler)
    
    # بدء البوت
    logger.info("Bot is starting...")
    
    # تشغيل Flask في خيط منفصل
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
