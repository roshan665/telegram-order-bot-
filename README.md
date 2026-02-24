# Telegram Order Bot 🤖

A feature-rich Telegram bot for managing customer orders with FAQ support, Excel storage, and owner notifications.

## Features ✨

- **📦 Step-by-step Order Taking**: Interactive conversation flow to collect customer information
- **💾 Excel Storage**: Automatic order storage in Excel format with auto-incrementing Order IDs
- **🔔 Owner Notifications**: Real-time order notifications sent to shop owner
- **❓ FAQ System**: Automated responses to common customer questions
- **✅ Order Confirmation**: Customers receive instant confirmation of their orders
- **🛡️ Error Handling**: Robust error handling and input validation

## Prerequisites 📋

- Python 3.8 or higher
- A Telegram account
- Basic knowledge of command line/terminal

## Installation Steps 🚀

### 1. Clone or Download the Project

```bash
cd d:\College\project_major
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `python-telegram-bot` - Telegram Bot API wrapper
- `pandas` - Excel data manipulation
- `openpyxl` - Excel file support
- `python-dotenv` - Environment variable management

### 3. Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions:
   - Choose a name for your bot (e.g., "My Shop Bot")
   - Choose a username (must end with 'bot', e.g., "myshop_order_bot")
4. **BotFather will give you a TOKEN** - Save this! It looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 4. Get Your Chat ID (For Owner Notifications)

To receive order notifications, you need your Telegram Chat ID:

**Method 1: Using @userinfobot**
1. Open Telegram and search for **@userinfobot**
2. Send any message to it
3. It will reply with your Chat ID (a number like `123456789`)

**Method 2: Using @raw_data_bot**
1. Search for **@raw_data_bot**
2. Send any message
3. Look for `"id":` in the response

**Method 3: Manual way**
1. Send a message to your bot first
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":123456789}`

### 5. Configure the Bot

**Option A: Using .env file (Recommended)**

1. Create a `.env` file in the project folder:

```bash
# Copy the example file
copy .env.example .env
```

2. Edit `.env` file with your actual credentials:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OWNER_CHAT_ID=123456789
```

**Option B: Directly edit config.py**

Open `config.py` and replace the placeholder values:

```python
BOT_TOKEN = 'YOUR_ACTUAL_BOT_TOKEN_HERE'
OWNER_CHAT_ID = 'YOUR_ACTUAL_CHAT_ID_HERE'
```

## Running the Bot 🏃

### Local Development

```bash
python bot.py
```

You should see:
```
Bot is starting...
```

### Test the Bot

1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. Try placing an order or asking a question!

## Bot Commands 📝

- `/start` - Welcome message with main menu
- `/cancel` - Cancel current order process
- `/help` - Show help and available commands

## How It Works 🔄

### Order Flow:
1. Customer clicks "Place Order"
2. Bot asks for Name → Phone → Product → Quantity → Address
3. Order is saved to `orders.xlsx` with auto-incremented Order ID
4. Customer receives confirmation
5. Owner gets notification with all order details

### FAQ System:
- Customer asks a question
- Bot checks predefined FAQ dictionary
- If match found, sends answer
- If not found, suggests contacting support

## Excel File Structure 📊

The bot creates `orders.xlsx` with these columns:

| Order ID | Name | Phone | Product | Quantity | Address | Date |
|----------|------|-------|---------|----------|---------|------|
| 1 | John Doe | +1234567890 | Laptop | 2 | 123 Main St | 2026-02-24 10:30:00 |

## Customization 🎨

### Adding More FAQs

Edit `bot.py` and add to the `FAQ_DICT`:

```python
FAQ_DICT = {
    "your new question": "Your answer here",
    "another question": "Another answer",
    # ... add more
}
```

### Changing Excel File Name

In `bot.py`, modify:
```python
EXCEL_FILE = "your_custom_name.xlsx"
```

### Customizing Messages

All messages are in the handler functions in `bot.py`. Search for the message you want to change and edit it.

## Deployment Options 🌐

### Option 1: VPS/Server (Recommended for Production)

**Using services like DigitalOcean, AWS EC2, Linode, etc.**

1. **Create a server** (Ubuntu recommended)

2. **Connect via SSH**:
```bash
ssh root@your_server_ip
```

3. **Install Python and dependencies**:
```bash
apt update
apt install python3 python3-pip -y
```

4. **Upload your bot files** (use FileZilla, SCP, or Git):
```bash
# Using Git
git clone your_repository_url
cd your_repository

# Or using SCP from your local machine
scp -r d:\College\project_major root@your_server_ip:/root/telegram_bot
```

5. **Install requirements**:
```bash
cd /root/telegram_bot
pip3 install -r requirements.txt
```

6. **Configure credentials** (create .env file on server)

7. **Run with screen/tmux** (keeps running after disconnect):
```bash
# Install screen
apt install screen -y

# Start a screen session
screen -S telegram_bot

# Run the bot
python3 bot.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r telegram_bot
```

8. **Or use systemd service** (auto-restart on failure):

Create `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Order Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/telegram_bot
ExecStart=/usr/bin/python3 /root/telegram_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl enable telegram-bot
systemctl start telegram-bot
systemctl status telegram-bot
```

### Option 2: PythonAnywhere (Free tier available)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files via Files tab
3. Open a Bash console
4. Install requirements: `pip install --user -r requirements.txt`
5. Create an "Always-on task" (paid) or use "Scheduled tasks" to keep bot running

### Option 3: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
worker: python bot.py
```
3. Deploy:
```bash
heroku login
heroku create your-bot-name
git push heroku main
heroku ps:scale worker=1
```

### Option 4: Railway

1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables in dashboard
4. Deploy automatically

### Option 5: Google Cloud Run / AWS Lambda

For serverless options, you'll need to modify the bot to use webhooks instead of polling.

## Keeping the Bot Running 24/7 ⏰

### On Windows (Local):
- **Option 1**: Keep your computer running with bot in terminal
- **Option 2**: Use Task Scheduler to auto-start on boot
- **Option 3**: Use NSSM (Non-Sucking Service Manager) to run as Windows service

### On Linux Server:
- **Recommended**: Use systemd service (see deployment section)
- **Alternative**: Use screen/tmux sessions
- **Alternative**: Use supervisor process manager

## Troubleshooting 🔧

### Bot doesn't respond:
- Check if bot is running (`python bot.py` should show "Bot is starting...")
- Verify BOT_TOKEN is correct
- Make sure you sent `/start` to the bot
- Check if bot username is correct

### Owner not receiving notifications:
- Verify OWNER_CHAT_ID is correct (it's a number, not username)
- Make sure you've sent at least one message to the bot
- Check bot.py logs for errors

### Excel file errors:
- Ensure the bot has write permissions in the directory
- Check if openpyxl is installed: `pip install openpyxl`
- Make sure no other program has orders.xlsx open

### Dependencies issues:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## File Structure 📁

```
project_major/
├── bot.py              # Main bot application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── .env.example       # Example environment file
├── README.md          # This file
└── orders.xlsx        # Generated automatically when first order is placed
```

## Security Best Practices 🔐

1. **Never share your BOT_TOKEN** - Anyone with it can control your bot
2. **Add to .gitignore**: 
   ```
   .env
   config.py
   orders.xlsx
   ```
3. **Use .env file** for credentials instead of hardcoding
4. **Backup orders.xlsx** regularly
5. **Use HTTPS** when deploying online

## Adding More Features 🚀

Some ideas to extend the bot:

- **Payment integration** (Stripe, PayPal)
- **Order status tracking** (/track command)
- **Admin commands** (view all orders, mark as completed)
- **Product catalog** with images
- **Multiple owners** (send notifications to multiple chat IDs)
- **Order cancellation** by customers
- **CSV export** option
- **Database integration** (SQLite, PostgreSQL)
- **Image upload** support for products

## Support 💬

If you encounter issues:
1. Check the logs in terminal
2. Review this README
3. Check [python-telegram-bot documentation](https://docs.python-telegram-bot.org/)
4. Search for error messages online

## License 📄

Free to use and modify for your projects.

## Author ✍️

Created for college project - Telegram Order Management Bot

---

**Happy Bot Development! 🎉**
