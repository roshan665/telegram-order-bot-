# Deployment Guide for Telegram Order Bot 🚀

This guide will help you deploy your bot on **PythonAnywhere** so it runs 24/7 and anyone can use it.

**Why PythonAnywhere?**
- ✅ Free tier available (great for starting)
- ✅ Persistent file storage (Excel files won't be lost)
- ✅ Easy web-based interface
- ✅ Perfect for Python bots

---

## Step-by-Step Deployment Guide 🐍

### Step 1: Sign Up for PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Pricing & signup"
3. Choose **Beginner Account (FREE)**
4. Create your account

### Step 2: Create GitHub Repository

Your code is already committed locally. Let's push it to GitHub:

1. **Create a New Repository on GitHub:**
   - Go to [github.com](https://github.com) and log in
   - Click the **"+"** icon (top right) → "New repository"
   - Name it: `telegram-order-bot` (or any name you like)
   - **Important:** Choose **Public** or **Private** based on your preference
   - **Don't** add README, .gitignore (we already have them)
   - Click "Create repository"

2. **GitHub will show you commands like these:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/telegram-order-bot.git
   git branch -M main
   git push -u origin main
   ```

3. **Run these commands in your PowerShell terminal:**
   
   Replace `YOUR_USERNAME` with your actual GitHub username:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/telegram-order-bot.git
   git branch -M main
   git push -u origin main
   ```
   
   You may be asked to log in to GitHub.

### Step 3: Clone Repository in PythonAnywhere

1. **Login to PythonAnywhere**
   - Go to your [PythonAnywhere Dashboard](https://www.pythonanywhere.com/user/)

2. **Open a Bash Console**
   - Click on "Consoles" tab at the top
   - Click "Bash" to start a new bash console

3. **Clone Your Repository**
   
   In the bash console, type:
   ```bash
   git clone https://github.com/YOUR_USERNAME/telegram-order-bot.git
   cd telegram-order-bot
   ```
   
   Replace `YOUR_USERNAME` with your actual GitHub username.
   
   **If your repo is private**, you'll need a Personal Access Token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` permissions
   - Use: `git clone https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/telegram-order-bot.git`

### Step 4: Install Dependencies

In the same bash console:

```bash
# Install required packages (takes 1-2 minutes)
pip3.10 install --user -r requirements.txt
```

Wait for installation to complete.

### Step 5: Configure Environment Variables

Create your `.env` file with your actual credentials:

```bash
# Create .env file
nano .env
```

Copy and paste this, replacing with your actual values:
```env
BOT_TOKEN=your_bot_token_from_botfather
OWNER_CHAT_ID=your_telegram_chat_id
SUPPORT_EMAIL=your_email@gmail.com
CONTACT_NUMBER=+91-your_phone_number
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_PASSWORD=your_gmail_app_password_16_chars
ORDER_NOTIFICATION_EMAIL=where_to_receive_orders@gmail.com
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

### Step 6: Test Your Bot

Test if everything works:

```bash
python3.10 bot.py
```

**You should see:**
- "Bot started successfully" message
- Your bot coming online on Telegram

**Test it:**
- Open Telegram
- Find your bot
- Send `/start` command

If it responds, great! Press `Ctrl + C` in the console to stop it.

### Step 7: Setup Always-On Task

**Important:** Free PythonAnywhere accounts have limitations. Choose one:

#### Option A: Scheduled Tasks (FREE) - Limited

Good if you don't need 24/7 operation:

1. Go to "Tasks" tab in PythonAnywhere dashboard
2. In "Scheduled tasks" section, add:
   ```
   python3.10 /home/YOUR_USERNAME/telegram-order-bot/bot.py
   ```
3. Set frequency (e.g., hourly or daily)
4. Click "Create"

**Limitation:** Bot only runs at scheduled times, not continuously.

#### Option B: Always-On Task ($5/month) - RECOMMENDED

For true 24/7 operation:

1. Go to "Account" tab
2. Upgrade to **"Hacker" plan ($5/month)**
3. After upgrading, go to "Tasks" tab
4. Create an **Always-on task:**
   - Command: `python3.10 /home/YOUR_USERNAME/telegram-order-bot/bot.py`
   - Click "Create"
5. Your bot will now run 24/7!

### Step 8: Monitor Your Bot

**View Logs in Real-Time:**

In a bash console:
```bash
cd telegram-order-bot
# If using always-on task, check server logs at "Tasks" tab
```

**Or check logs in PythonAnywhere:**
1. Go to "Tasks" tab
2. Click on your task name
3. Click "Log" to see output and errors

### Step 9: Managing Excel Files

Your Excel files (`orders.xlsx`, `customers.xlsx`) will be created automatically and persist.

**To download/view them:**
1. Go to "Files" tab
2. Navigate to `/home/YOUR_USERNAME/telegram-order-bot/`
3. Click on file names to download or view

**Backup regularly:**
- Download Excel files weekly
- Keep local copies as backup

---

## Alternative Deployment Options

If PythonAnywhere doesn't work for you:

### Option 2: Railway.app 🚂
**Pros:** Free 500 hours/month, super easy  
**Cons:** Files don't persist (Excel lost on restart)

Quick steps: Connect GitHub → Deploy → Add env variables

### Option 3: Render.com 🎨
**Pros:** Free tier, automatic SSL  
**Cons:** Cold starts, files don't persist

Quick steps: Create Background Worker → Connect repo → Deploy

### Option 4: DigitalOcean 💧
**Pros:** Full control, very reliable ($6/month)  
**Cons:** Requires Linux knowledge

Quick steps: Create Droplet → Setup systemd service → Run 24/7

---

## Security Checklist 🔒

✅ `.env` file is NOT uploaded to GitHub (protected by .gitignore)  
✅ Excel files are NOT uploaded to GitHub  
✅ Never share your BOT_TOKEN publicly  
✅ Use Gmail App Password (not regular password)  
✅ Keep your GitHub repository private if it contains sensitive code  

---

## Troubleshooting Common Issues 🔧

### Issue 1: "Authentication Error" when bot starts
**Solution:** Check your `BOT_TOKEN` in .env file. Get new token from @BotFather if needed.

### Issue 2: Email not sending
**Solution:** 
- Use Gmail App Password (16 characters, no spaces)
- Generate at: https://myaccount.google.com/apppasswords
- Enable 2-Factor Authentication first

### Issue 3: Bot not responding to commands
**Solution:**
- Check logs for errors
- Verify bot is running (check Task status)
- Test with `/start` command
- Make sure bot isn't running elsewhere

### Issue 4: "Module not found" error
**Solution:**
```bash
pip3.10 install --user -r requirements.txt
```

### Issue 5: Excel file permission error
**Solution:**
```bash
chmod 755 /home/YOUR_USERNAME/telegram-order-bot/
```

### Issue 6: Git push authentication failed
**Solution:** Use Personal Access Token instead of password:
- GitHub → Settings → Developer settings → Personal access tokens
- Generate new token with `repo` scope
- Use token as password when pushing

---

## Updating Your Bot After Deployment 🔄

When you make changes to your code:

### Local Changes:
```powershell
# In your project directory
git add .
git commit -m "Description of your changes"
git push
```

### Update on PythonAnywhere:
1. Open bash console
2. Run:
   ```bash
   cd telegram-order-bot
   git pull
   ```
3. Restart your bot:
   - Go to "Tasks" tab
   - Click "Reload" button next to your task

---

## Next Steps After Deployment ✅

1. ✅ Test all bot commands:
   - `/start` - Welcome message
   - `/order` - Place order
   - `/faq` - View FAQs
   - `/help` - Get help
   
2. ✅ Place a test order to verify:
   - Excel file is created
   - Email notification is sent
   - Order ID increments correctly

3. ✅ Share your bot:
   - Bot link: `t.me/YOUR_BOT_USERNAME`
   - Share with customers
   
4. ✅ Monitor regularly:
   - Check logs for errors
   - Download Excel files as backup
   - Monitor bot performance

5. ✅ Promote your bot:
   - Add bot link to your website
   - Share on social media
   - Add to your business cards

---

## Monitoring & Maintenance 📊

### Daily:
- Check if bot is online (send a test message)
- Review new orders in Excel file

### Weekly:
- Download and backup Excel files
- Check error logs
- Test all bot commands

### Monthly:
- Review PythonAnywhere usage
- Update bot code if needed
- Clean up old data if necessary

---

## Cost Summary 💰

| Plan | Cost | Features |
|------|------|----------|
| **Free Tier** | $0 | Scheduled tasks only, good for testing |
| **Hacker Plan** | $5/month | Always-on tasks, 24/7 bot operation ⭐ |
| **Web Developer** | $12/month | More CPU, multiple bots |

**Recommended:** Start with free tier to test, then upgrade to Hacker ($5/month) for production.

---

## Comparison with Other Platforms

| Platform | Cost | Files Persist | Ease of Use | Best For |
|----------|------|---------------|-------------|----------|
| **PythonAnywhere** | **$5/mo** | **✅ Yes** | ⭐⭐⭐⭐ | **Excel storage** ⭐ |
| Railway | Free* | ❌ No | ⭐⭐⭐⭐⭐ | Quick testing |
| Render | Free* | ❌ No | ⭐⭐⭐⭐ | Alternative |
| DigitalOcean | $6/mo | ✅ Yes | ⭐⭐⭐ | Production scale |

*Limited free tier hours

---

## Support & Resources 📚

- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **python-telegram-bot Docs:** https://docs.python-telegram-bot.org/
- **GitHub Docs:** https://docs.github.com/

---

## Why PythonAnywhere is Perfect for Your Bot 🌟

✅ **Excel files persist** - Orders won't be lost  
✅ **Affordable** - Only $5/month for 24/7  
✅ **Easy management** - Web interface, no Linux knowledge needed  
✅ **Reliable** - 99.9% uptime  
✅ **Backup friendly** - Easy to download files  
✅ **Python optimized** - Made for Python projects  

---

## Summary 📝

**Setup Time:** ~15-20 minutes  
**Cost:** $0 (limited) or $5/month (24/7)  
**Difficulty:** Easy ⭐⭐⭐⭐☆  
**Recommended For:** Small to medium sized bots with file storage needs  

Your bot will be accessible to anyone with the link `t.me/YOUR_BOT_USERNAME` and will help customers place orders 24/7!

Good luck with your deployment! 🚀

---

*Need help? Check the troubleshooting section or PythonAnywhere's help forum.*
