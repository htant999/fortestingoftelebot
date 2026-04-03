from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import datetime
import os

# ---------------- CONFIG ----------------
TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 8342806850  # Replace with your Telegram ID

# ---------------- PRODUCTS ----------------
products = [
    {"name": "Fried Rice", "price": 3000, "image": "fried_rice.png"},
    {"name": "Noodles", "price": 2500, "image": "noodles.png"},
    {"name": "Coke", "price": 1000, "image": "coke.png"},
    {"name": "Water", "price": 500, "image": "water.png"},
]

# ---------------- INITIALIZE ----------------
def init_user(context):
    if "cart" not in context.user_data:
        context.user_data["cart"] = []
    if "ordering" not in context.user_data:
        context.user_data["ordering"] = False
    if "phone" not in context.user_data:
        context.user_data["phone"] = None
    if "address" not in context.user_data:
        context.user_data["address"] = None

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_user(context)
    keyboard = [
        [InlineKeyboardButton(f"{p['name']} - {p['price']}", callback_data=p['name'])] for p in products
    ]
    keyboard.append([InlineKeyboardButton("🛒 Checkout", callback_data="checkout")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to our shop 🛒\nSelect items below:", reply_markup=reply_markup)

# ---------------- BUTTON HANDLER ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_user(context)
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == "checkout":
        if not context.user_data["cart"]:
            await query.edit_message_text("Your cart is empty ❌")
            return
        context.user_data["ordering"] = True
        await query.edit_message_text("Please enter your phone number 📞:")
        return

    # Add product to cart
    for p in products:
        if p["name"] == data:
            context.user_data["cart"].append(f"{p['name']} - {p['price']}")
            await query.answer(f"Added {p['name']} ✅", show_alert=True)
            return

# ---------------- MESSAGE HANDLER ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init_user(context)
    if context.user_data.get("ordering") and context.user_data.get("phone") is None:
        context.user_data["phone"] = update.message.text
        await update.message.reply_text("Please enter your delivery address 📍:")
        return

    if context.user_data.get("ordering") and context.user_data.get("address") is None:
        context.user_data["address"] = update.message.text

        cart = context.user_data["cart"]
        phone = context.user_data["phone"]
        address = context.user_data["address"]
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        final_text = f"""
🛒 New Order
Name: {update.message.from_user.first_name}
Time: {time}
Phone: {phone}
Address: {address}

Items:
{chr(10).join(cart)}
"""

        # Send to owner
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=final_text)
        except Exception as e:
            print(f"Failed to send order: {e}")

        # Save locally
        with open("orders.txt", "a", encoding="utf-8") as f:
            f.write(final_text + "\n-----------------\n")

        # Confirm to customer
        await update.message.reply_text("✅ Order placed! We will contact you soon.")

        # Reset user data
        context.user_data["cart"] = []
        context.user_data["ordering"] = False
        context.user_data["phone"] = None
        context.user_data["address"] = None

    else:
        await update.message.reply_text("Please use the menu 👇 or /start to begin")

# ---------------- ERROR HANDLER ----------------
async def error_handler(update, context):
    print(f"Error: {context.error}")

# ---------------- RUN BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_error_handler(error_handler)

app.run_polling(timeout=30)
