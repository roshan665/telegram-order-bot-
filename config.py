"""
Configuration file for Telegram Bot
Store your sensitive information here.

IMPORTANT: Never commit this file with real credentials to version control!
Add config.py to .gitignore
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Token from BotFather
# Get it from: https://t.me/BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Owner's Telegram Chat ID for receiving order notifications
# Get it from: https://t.me/userinfobot
# Just send any message to @userinfobot and it will reply with your chat ID
OWNER_CHAT_ID = os.getenv('OWNER_CHAT_ID')

# Support contact information
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@yourshop.com')
CONTACT_NUMBER = os.getenv('CONTACT_NUMBER', '+1-234-567-8900')

# Email Configuration for sending order confirmations
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ORDER_NOTIFICATION_EMAIL = os.getenv('ORDER_NOTIFICATION_EMAIL', 'as1917378@gmail.com')

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("❌ ERROR: BOT_TOKEN not set! Please add it to .env file")

if not OWNER_CHAT_ID:
    raise ValueError("❌ ERROR: OWNER_CHAT_ID not set! Please add it to .env file")

print("✅ Configuration loaded successfully from .env file")
