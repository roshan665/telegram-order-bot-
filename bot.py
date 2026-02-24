"""
Telegram Bot for Order Management with FAQ System
Features:
- Step-by-step order taking with conversation flow
- Excel storage for orders
- Owner notifications
- FAQ system
- Command handling
"""

import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import (
    BOT_TOKEN, 
    OWNER_CHAT_ID, 
    SUPPORT_EMAIL, 
    CONTACT_NUMBER,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_PASSWORD,
    ORDER_NOTIFICATION_EMAIL
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states for order flow
NAME, PHONE, ADDRESS, PRODUCT, QUANTITY, ADD_MORE, REVIEW_CART, CONFIRM_ORDER = range(8)

# Excel file configuration
EXCEL_FILE = "orders.xlsx"
CUSTOMER_FILE = "customers.xlsx"

# FAQ Dictionary - Add more questions and answers as needed
FAQ_DICT = {
    "delivery time": "We typically deliver within 3-5 business days for local orders and 7-10 days for international orders.",
    "return policy": "We accept returns within 30 days of purchase. Items must be in original condition with tags attached.",
    "payment methods": "We accept credit cards, debit cards, PayPal, and bank transfers.",
    "shipping cost": "Shipping is free for orders above $50. For orders below $50, we charge a flat rate of $5.",
    "contact": f"You can contact us at {SUPPORT_EMAIL} or call us at {CONTACT_NUMBER}.",
    "working hours": "Our customer support is available Monday to Friday, 9 AM to 6 PM EST.",
}

# Grocery Items List with Prices (Indian Rupees) - Customers can select from these items
GROCERY_ITEMS = {
    "🧼 Bathing Soap": 35,
    "🛁 Bathing Bar": 62,
    "🪥 Dentassure Toothpaste": 65,
    "🪥 Tooth Brush": 235,
    "🫖 Zeta Tea": 107,
    "☕ Zeta Coffee": 158,
    "🫙 Rice Bran Cooking Oil": 295,
    "🧴 Shampoo": 163,
    "🧴 Hair Oil": 165,
    "🧴 Hair Conditioner": 208,
    "🧴 Face Wash": 146,
    "💆 Fairness Cream": 169,
    "🧴 Hand Wash": 118,
    "🪒 Shaving Cream": 101,
    "💨 Body Talc": 52,
    "🌬️ Deo (Men or Women)": 163,
    "🧴 Body Lotion": 191,
    "🧼 Liquid Detergent": 321,
    "🍽️ Dish Wash Liquid": 177,
    "🧹 Floor Cleaner": 186,
    "🥣 Enerva Breakfast": 299,
    "🌿 Spirulina": 350,
    "🫙 Flax Oil": 515,
}


def get_next_order_id():
    """
    Get the next order ID by checking the existing Excel file.
    If file doesn't exist, return 1.
    """
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            if len(df) > 0:
                return df['Order ID'].max() + 1
            else:
                return 1
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return 1
    return 1


def get_customer_info(user_id):
    """
    Get customer information from customer database.
    Returns customer data if exists, None otherwise.
    """
    if os.path.exists(CUSTOMER_FILE):
        try:
            df = pd.read_excel(CUSTOMER_FILE)
            customer = df[df['User ID'] == str(user_id)]
            if not customer.empty:
                return customer.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error reading customer file: {e}")
    return None


def save_customer_info(user_id, name, phone, address):
    """
    Save or update customer information in database.
    """
    try:
        customer_data = {
            'User ID': str(user_id),
            'Name': name,
            'Phone': phone,
            'Address': address,
            'Last Order Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if os.path.exists(CUSTOMER_FILE):
            df = pd.read_excel(CUSTOMER_FILE)
            # Check if customer exists
            if str(user_id) in df['User ID'].values:
                # Update existing customer
                df.loc[df['User ID'] == str(user_id), ['Name', 'Phone', 'Address', 'Last Order Date']] = [
                    name, phone, address, customer_data['Last Order Date']
                ]
            else:
                # Add new customer
                new_customer = pd.DataFrame([customer_data])
                df = pd.concat([df, new_customer], ignore_index=True)
            df.to_excel(CUSTOMER_FILE, index=False)
        else:
            # Create new file
            df = pd.DataFrame([customer_data])
            df.to_excel(CUSTOMER_FILE, index=False)
        
        logger.info(f"Customer {user_id} info saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving customer info: {e}")
        return False


def send_order_email(order_id, customer_name, customer_phone, products_list, address, total_price):
    """
    Send order confirmation email to the specified email address with prices.
    """
    if not EMAIL_PASSWORD:
        logger.warning("⚠️  Email password not configured. Skipping email notification.")
        logger.warning("⚠️  Set EMAIL_PASSWORD in .env file to enable email notifications.")
        return False
    
    if not SUPPORT_EMAIL or "@" not in SUPPORT_EMAIL:
        logger.error(f"❌ Invalid SUPPORT_EMAIL: {SUPPORT_EMAIL}")
        return False
    
    if not ORDER_NOTIFICATION_EMAIL or "@" not in ORDER_NOTIFICATION_EMAIL:
        logger.error(f"❌ Invalid ORDER_NOTIFICATION_EMAIL: {ORDER_NOTIFICATION_EMAIL}")
        return False
    
    try:
        logger.info(f"📧 Attempting to send email from {SUPPORT_EMAIL} to {ORDER_NOTIFICATION_EMAIL}")
        logger.info(f"📧 SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SUPPORT_EMAIL
        msg['To'] = ORDER_NOTIFICATION_EMAIL
        msg['Subject'] = f'New Order #{order_id} from {customer_name}'
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #4CAF50;">🔔 New Order Received!</h2>
            
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px;">
                <h3>Order Details:</h3>
                <p><strong>📋 Order ID:</strong> #{order_id}</p>
                <p><strong>👤 Customer Name:</strong> {customer_name}</p>
                <p><strong>📱 Phone:</strong> {customer_phone}</p>
                <p><strong>📍 Delivery Address:</strong> {address}</p>
                
                <h3>📦 Products Ordered:</h3>
                <ul>
                    {products_list}
                </ul>
                
                <h3 style="color: #4CAF50;">💰 Order Total: ₹{total_price:.0f}</h3>
                
                <p><strong>📅 Order Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <p style="margin-top: 20px; color: #666;">
                This is an automated notification from your Telegram Order Bot.
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        logger.info("🔐 Connecting to SMTP server...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            logger.info("🔒 Starting TLS encryption...")
            server.starttls()
            logger.info(f"🔑 Logging in with email: {SUPPORT_EMAIL}")
            server.login(SUPPORT_EMAIL, EMAIL_PASSWORD)
            logger.info("📤 Sending email message...")
            server.send_message(msg)
        
        logger.info(f"✅ Order confirmation email sent successfully for order #{order_id}")
        logger.info(f"✅ Email sent to: {ORDER_NOTIFICATION_EMAIL}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Email authentication failed: {e}")
        logger.error("❌ Check your EMAIL_PASSWORD or SUPPORT_EMAIL in .env file")
        logger.error("❌ Make sure you're using a Gmail App Password, not your regular password")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error occurred: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send order confirmation email: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        return False


def save_order_to_excel(order_data):
    """
    Save order data to Excel file.
    Creates file with headers if it doesn't exist.
    """
    try:
        # Prepare the order data
        order_df = pd.DataFrame([order_data])
        
        # Check if file exists
        if os.path.exists(EXCEL_FILE):
            # Append to existing file
            existing_df = pd.read_excel(EXCEL_FILE)
            updated_df = pd.concat([existing_df, order_df], ignore_index=True)
            updated_df.to_excel(EXCEL_FILE, index=False)
        else:
            # Create new file with headers
            order_df.to_excel(EXCEL_FILE, index=False)
        
        logger.info(f"Order {order_data['Customer ID']} saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving order to Excel: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    Show welcome message with options.
    """
    user = update.effective_user
    keyboard = [
        ["📦 Place Order"],
        ["❓ Ask Question"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    welcome_message = (
        f"👋 Hello {user.first_name}! Welcome to our store!\n\n"
        "I'm here to help you with:\n"
        "• 📦 Placing orders\n"
        "• ❓ Answering your questions\n\n"
        "What would you like to do?"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /cancel command.
    Cancel current order conversation.
    """
    context.user_data.clear()
    return await back_to_menu(update, context)


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Return user to main menu.
    """
    keyboard = [
        ["📦 Place Order"],
        ["❓ Ask Question"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🏠 Back to Main Menu\n\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start ordering directly using Telegram ID.
    NO personal details needed - just start selecting items!
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or f"User{user_id}"
    
    # Initialize cart & user data
    context.user_data['cart'] = []
    context.user_data['user_id'] = user_id
    context.user_data['username'] = username
    
    logger.info(f"📦 Order started by Telegram ID: {user_id} (@{username})")
    
    # SKIP EVERYTHING - GO DIRECTLY TO PRODUCTS!
    keyboard = []
    items_list = list(GROCERY_ITEMS.keys())
    for i in range(0, len(items_list), 2):
        row = items_list[i:i+2]
        keyboard.append(row)
    keyboard.append(["🛒 View Cart", "🔙 Back to Menu"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Welcome @{username}! (ID: {user_id})\n\n"
        "🛒 Select items you want to order:"
    )
    await update.message.reply_text("Our products:", reply_markup=reply_markup)
    return PRODUCT


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    NEW CUSTOMERS ONLY: Store customer name and ask for phone number.
    Returning customers skip this state entirely (see start_order).
    """
    # Check for back button
    if update.message.text == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    
    # Store name for new customer
    keyboard = [["🔙 Back to Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Thank you, {update.message.text}! 📝\n\n"
        "Please provide your phone number:",
        reply_markup=reply_markup
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store phone number and ask for address (NEW CUSTOMERS ONLY).
    """
    # Back to menu
    if update.message.text == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    
    # Store phone
    context.user_data['phone'] = update.message.text
    
    # Ask for address
    keyboard = [["🔙 Back to Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"📱 Phone saved!\n\n"
        "📍 Your delivery address?",
        reply_markup=reply_markup
    )
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store address, save customer info to Excel, then show products.
    NEW CUSTOMERS ONLY - Returning customers skip directly to products.
    """
    # Back to menu
    if update.message.text == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    
    # Store address
    context.user_data['address'] = update.message.text
    
    # 💾 SAVE CUSTOMER TO EXCEL NOW
    user_id = context.user_data['user_id']
    save_customer_info(
        user_id,
        context.user_data['name'],
        context.user_data['phone'],
        context.user_data['address']
    )
    logger.info(f"✅ NEW customer {user_id} saved to database")
    
    # Now show products
    keyboard = []
    items_list = list(GROCERY_ITEMS.keys())
    for i in range(0, len(items_list), 2):
        row = items_list[i:i+2]
        keyboard.append(row)
    keyboard.append(["🛒 View Cart", "🔙 Back to Menu"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "✅ All details saved!\n\n"
        "🛒 Now select items to order:",
        reply_markup=reply_markup
    )
    return PRODUCT


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display grocery items for selection.
    """
    # Create keyboard with grocery items (2 items per row)
    keyboard = []
    items_list = list(GROCERY_ITEMS.keys())
    for i in range(0, len(items_list), 2):
        row = items_list[i:i+2]
        keyboard.append(row)
    keyboard.append(["🛒 View Cart", "🔙 Back to Menu"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    cart_info = ""
    total_items = 0
    if context.user_data.get('cart'):
        total_items = sum([item['quantity'] for item in context.user_data['cart']])
        cart_info = f"\n\n🛒 Items in cart: {len(context.user_data['cart'])} product(s), {total_items} units"
    
    await update.message.reply_text(
        "🛒 Select products from our grocery list:{cart_info}".format(cart_info=cart_info),
        reply_markup=reply_markup
    )
    return PRODUCT


async def get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle product selection from the grocery list.
    """
    selected_text = update.message.text
    
    # Back to menu
    if selected_text == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    
    # View cart before checkout
    if selected_text == "🛒 View Cart":
        return await review_cart(update, context)
    
    # Validate if selected product is from the list
    if selected_text not in GROCERY_ITEMS:
        # Show products again if invalid selection
        keyboard = []
        items_list = list(GROCERY_ITEMS.keys())
        for i in range(0, len(items_list), 2):
            row = items_list[i:i+2]
            keyboard.append(row)
        keyboard.append(["🛒 View Cart", "🔙 Back to Menu"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "⚠️ Please select a valid item:",
            reply_markup=reply_markup
        )
        return PRODUCT
    
    # Valid product - ask for quantity
    context.user_data['current_product'] = selected_text
    
    keyboard = [["🔙 Back to Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    price = GROCERY_ITEMS[selected_text]
    await update.message.reply_text(
        f"✅ {selected_text}\n💰 Price: ₹{price:.0f}\n\n"
        "How many?",
        reply_markup=reply_markup
    )
    return QUANTITY


async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Store quantity, add to cart, and ask if want more items.
    """
    # Check for back button
    if update.message.text == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    
    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            keyboard = [["🔙 Back to Menu"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "❌ Please enter a valid positive number for quantity:",
                reply_markup=reply_markup
            )
            return QUANTITY
        
        # Add item to cart
        cart_item = {
            'product': context.user_data['current_product'],
            'quantity': quantity
        }
        context.user_data['cart'].append(cart_item)
        
        # Ask if want more items
        keyboard = [
            ["➕ Add More Items"],
            ["✅ Checkout"],
            ["🛒 View Cart"],
            ["🔙 Back to Menu"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ Added {quantity} x {context.user_data['current_product']} to cart!\n\n"
            f"🛒 Total items in cart: {len(context.user_data['cart'])}\n\n"
            "What would you like to do next?",
            reply_markup=reply_markup
        )
        return ADD_MORE
        
    except ValueError:
        keyboard = [["🔙 Back to Menu"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "❌ Please enter a valid number for quantity:",
            reply_markup=reply_markup
        )
        return QUANTITY


async def add_more_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle add more items or checkout.
    """
    choice = update.message.text
    
    if choice == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    elif choice == "➕ Add More Items":
        return await show_products(update, context)
    elif choice == "🛒 View Cart":
        return await review_cart(update, context)
    elif choice == "✅ Checkout":
        return await review_cart(update, context)
    else:
        return ADD_MORE


async def review_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show cart contents with prices and ask for confirmation.
    """
    cart = context.user_data.get('cart', [])
    
    if not cart:
        keyboard = [
            ["➕ Add Items"],
            ["🔙 Back to Menu"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "🛒 Your cart is empty!\n\n"
            "Would you like to add some items?",
            reply_markup=reply_markup
        )
        return ADD_MORE
    
    # Build cart summary with prices
    cart_summary = "🛒 YOUR CART:\n\n"
    total_price = 0
    for idx, item in enumerate(cart, 1):
        price = GROCERY_ITEMS.get(item['product'], 0)
        item_total = price * item['quantity']
        total_price += item_total
        cart_summary += f"{idx}. {item['product']}\n   Qty: {item['quantity']} × ₹{price:.0f} = ₹{item_total:.0f}\n\n"
    
    cart_summary += f"💰 TOTAL: ₹{total_price:.0f}\n\n"
    cart_summary += f"📦 Total Items: {len(cart)}\n"
    cart_summary += f"🆔 Order By: @{context.user_data.get('username', 'User')} (ID: {context.user_data['user_id']})\n\n"
    cart_summary += "Confirm your order?"
    
    context.user_data['total_price'] = total_price
    
    keyboard = [
        ["✅ Confirm Order"],
        ["➕ Add More Items"],
        ["❌ Clear Cart"],
        ["🔙 Back to Menu"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(cart_summary, reply_markup=reply_markup)
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle order confirmation, cancellation, or cart modification.
    """
    choice = update.message.text
    
    if choice == "🔙 Back to Menu":
        context.user_data.clear()
        return await back_to_menu(update, context)
    elif choice == "➕ Add More Items":
        # Create keyboard with grocery items (2 items per row)
        keyboard = []
        items_list = list(GROCERY_ITEMS.keys())
        for i in range(0, len(items_list), 2):
            row = items_list[i:i+2]
            keyboard.append(row)
        keyboard.append(["🛒 View Cart", "🔙 Back to Menu"])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        cart_info = ""
        total_items = 0
        if context.user_data.get('cart'):
            total_items = sum([item['quantity'] for item in context.user_data['cart']])
            cart_info = f"\n\n🛒 Items in cart: {len(context.user_data['cart'])} product(s), {total_items} units"
        
        await update.message.reply_text(
            f"➕ Add More Items...{cart_info}",
            reply_markup=reply_markup
        )
        return PRODUCT
    elif choice == "❌ Clear Cart":
        context.user_data['cart'] = []
        keyboard = [
            ["➕ Add Items"],
            ["🔙 Back to Menu"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "🗑️ Cart cleared!\n\n"
            "Would you like to add some items?",
            reply_markup=reply_markup
        )
        return ADD_MORE
    elif choice == "✅ Confirm Order":
        # Process the order
        cart = context.user_data['cart']
        order_id = get_next_order_id()
        
        # Prepare order data for each item (only save products with prices)
        all_orders_saved = True
        for item in cart:
            # Skip products without prices
            if item['product'] not in GROCERY_ITEMS:
                logger.warning(f"⚠️ Skipping product '{item['product']}' - not in price list")
                continue
            
            order_data = {
                'Customer ID': context.user_data['user_id'],
                'Username': context.user_data.get('username', 'Unknown'),
                'Product': item['product'],
                'Quantity': item['quantity'],
                'Price': GROCERY_ITEMS[item['product']],
                'Total': GROCERY_ITEMS[item['product']] * item['quantity'],
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if not save_order_to_excel(order_data):
                all_orders_saved = False
                break
        
        if all_orders_saved:
            # Build order confirmation message with prices
            # Only include products that have prices
            total_price = 0
            products_list = ""
            for item in cart:
                price = GROCERY_ITEMS.get(item['product'], None)
                # Skip products without prices
                if price is None:
                    logger.warning(f"⚠️ Product '{item['product']}' has no price, skipping from order")
                    continue
                
                item_total = price * item['quantity']
                total_price += item_total
                products_list += f"  • {item['product']}\n    ₹{price:.0f} × {item['quantity']} = ₹{item_total:.0f}\n"
            
            confirmation_msg = (
                f"✅ ORDER CONFIRMED!\n\n"
                f"🆔 Order ID: {context.user_data['user_id']}\n"
                f"📦 Products:\n{products_list}\n"
                f"💰 TOTAL: ₹{total_price:.0f}\n"
                f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Thank you for your order! 🎉"
            )
            
            # Send confirmation to customer
            keyboard = [["📦 Place Order"], ["❓ Ask Question"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(confirmation_msg, reply_markup=reply_markup)
            
            # Notify owner
            owner_message = (
                f"🔔 NEW ORDER RECEIVED!\n\n"
                f"🆔 Order ID: {context.user_data['user_id']}\n"
                f"👤 Customer: @{context.user_data.get('username', 'User')}\n"
                f"📦 Products:\n{products_list}\n"
                f"💰 TOTAL: ₹{total_price:.0f}\n"
                f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            try:
                await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=owner_message)
                logger.info(f"Owner notified about order {context.user_data['user_id']}")
            except Exception as e:
                logger.error(f"Failed to notify owner: {e}")
            
            # Send email notification with prices (only products with prices)
            products_html = ""
            for item in cart:
                price = GROCERY_ITEMS.get(item['product'], None)
                # Skip products without prices
                if price is None:
                    continue
                
                item_total = price * item['quantity']
                products_html += f"<li>{item['product']} (₹{price:.0f} × {item['quantity']}) = ₹{item_total:.0f}</li>"
            
            send_order_email(
                context.user_data['user_id'],
                context.user_data.get('username', 'User'),
                str(context.user_data['user_id']),
                products_html,
                f"Telegram ID: {context.user_data['user_id']}",
                total_price
            )
        else:
            keyboard = [["📦 Place Order"], ["❓ Ask Question"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "❌ Sorry, there was an error processing your order. Please try again or contact support.",
                reply_markup=reply_markup
            )
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END
    else:
        return CONFIRM_ORDER


def check_faq(message_text):
    """
    Check if the message matches any FAQ question.
    Returns the answer if found, None otherwise.
    """
    message_lower = message_text.lower().strip()
    
    # Check for exact or partial matches
    for question, answer in FAQ_DICT.items():
        if question in message_lower:
            return answer
    
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle regular messages (non-command, non-conversation).
    Check FAQ or provide default response.
    """
    message_text = update.message.text
    
    # Check if message is a button press
    if message_text == "📦 Place Order":
        return await start_order(update, context)
    elif message_text == "❓ Ask Question":
        keyboard = [["🔙 Back to Menu"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "❓ Sure! What would you like to know?\n\n"
            "You can ask about:\n"
            "• Delivery time\n"
            "• Return policy\n"
            "• Payment methods\n"
            "• Shipping cost\n"
            "• Contact information\n"
            "• Working hours",
            reply_markup=reply_markup
        )
        return
    elif message_text == "🔙 Back to Menu":
        return await back_to_menu(update, context)
    
    # Check FAQ
    answer = check_faq(message_text)
    
    keyboard = [["🔙 Back to Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if answer:
        await update.message.reply_text(f"💡 {answer}", reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            f"🤔 I'm not sure about that. Please contact us at {SUPPORT_EMAIL}\n\n"
            "Or type /start to place an order or ask a different question.",
            reply_markup=reply_markup
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command.
    Show available commands and features.
    """
    keyboard = [["🔙 Back to Menu"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    help_text = (
        "🤖 Bot Commands:\n\n"
        "/start - Start the bot and see options\n"
        "/cancel - Cancel current order\n"
        "/help - Show this help message\n\n"
        "Features:\n"
        "• Place orders from grocery list\n"
        "• Get answers to common questions\n"
        "• Receive order confirmations\n\n"
        f"Need help? Contact {SUPPORT_EMAIL} or call {CONTACT_NUMBER}"
    )
    await update.message.reply_text(help_text, reply_markup=reply_markup)


def main():
    """
    Main function to start the bot.
    """
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler for order flow
    order_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📦 Place Order$"), start_order),
        ],
        states={
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            ADD_MORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_more_handler)],
            REVIEW_CART: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_cart)],
            CONFIRM_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_order)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(order_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
