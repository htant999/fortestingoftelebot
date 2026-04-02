from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import datetime

# ------------------ CONFIG ------------------
TOKEN = "8724808752:AAEmeMS4l4EuLQps07iCu0VXrLPy4hT-N3s"  # Replace with your bot token
OWNER_ID = 8342806850      # Replace with your Telegram numeric ID

# ------------------ MENU ------------------
menu_keyboard = [
    ["🍛 Fried Rice - 3000", "🍜 Noodles - 2500"],
    ["🥤 Coke - 1000", "💧 Water - 500"],
    ["🛒 Checkout"]
]

# ------------------ START ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []
    context.user_data["ordering"] = False
    context.user_data["phone"] = None
    context.user_data["address"] = None

    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to our shop 🛒\nSelect items below 👇",
        reply_markup=reply_markup
    )

# ------------------ HANDLE MESSAGES ------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    # ---------- ADD TO CART ----------
    if "Fried Rice" in text:
        context.user_data["cart"].append("Fried Rice - 3000")
        await update.message.reply_text("Added Fried Rice ✅")

    elif "Noodles" in text:
        context.user_data["cart"].append("Noodles - 2500")
        await update.message.reply_text("Added Noodles ✅")

    elif "Coke" in text:
        context.user_data["cart"].append("Coke - 1000")
        await update.message.reply_text("Added Coke ✅")

    elif "Water" in text:
        context.user_data["cart"].append("Water - 500")
        await update.message.reply_text("Added Water ✅")

    # ---------- CHECKOUT ----------
    elif "Checkout" in text:
        cart = context.user_data.get("cart", [])
        if not cart:
            await update.message.reply_text("Your cart is empty ❌")
            return

        context.user_data["ordering"] = True
        await update.message.reply_text("Please enter your phone number 📞:")

    # ---------- PHONE ----------
    elif context.user_data.get("ordering") and context.user_data.get("phone") is None:
        context.user_data["phone"] = text
        await update.message.reply_text("Please enter your delivery address 📍:")

    # ---------- ADDRESS & SEND ORDER ----------
    elif context.user_data.get("ordering") and context.user_data.get("address") is None:
        context.user_data["address"] = text

        cart = context.user_data.get("cart")
        phone = context.user_data.get("phone")
        address = context.user_data.get("address")
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare final order text
        final_text = f"""
🛒 New Order
Name: {user.first_name}
Time: {time}
Phone: {phone}
Address: {address}

Items:
{chr(10).join(cart)}
"""

        # ---------- SEND TO OWNER ----------
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=final_text)
        except Exception as e:
            print(f"Failed to send order to owner: {e}")

        # ---------- SAVE TO FILE ----------
        with open("orders.txt", "a", encoding="utf-8") as f:
            f.write(final_text + "\n-----------------\n")

        # ---------- CONFIRM TO CUSTOMER ----------
        await update.message.reply_text("✅ Order placed! We will contact you soon.")

        # Reset user data
        context.user_data["cart"] = []
        context.user_data["ordering"] = False
        context.user_data["phone"] = None
        context.user_data["address"] = None

    else:
        await update.message.reply_text("Please select from menu 👇")

# ------------------ ERROR HANDLER ------------------
async def error_handler(update, context):
    print(f"Error: {context.error}")

# ------------------ RUN BOT ------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_error_handler(error_handler)

# Run bot with network retry
app.run_polling(timeout=30)