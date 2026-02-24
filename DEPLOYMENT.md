# Deployment Guide for Telegram Order Bot 🚀

This guide covers multiple ways to deploy your bot so it runs 24/7 and anyone can use it.

---

## Option 1: Railway.app (RECOMMENDED - Easy & Free) 🚂

Railway offers 500 free hours/month and automatic deployments.

### Steps:

1. **Create a GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
   - Go to [GitHub](https://github.com) and create a new repository
   - Push your code:
     ```bash
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
     git branch -M main
     git push -u origin main
     ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Click "Add Variables" and add:
     ```
     BOT_TOKEN=your_bot_token_here
     OWNER_CHAT_ID=your_chat_id_here
     SUPPORT_EMAIL=your_email@gmail.com
     CONTACT_NUMBER=your_phone_number
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     EMAIL_PASSWORD=your_gmail_app_password
     ORDER_NOTIFICATION_EMAIL=notification_email@gmail.com
     ```
   - Railway will automatically deploy your bot!

3. **Check Logs**
   - Go to your project on Railway
   - Click on "Deployments" to see logs
   - Your bot should be running 24/7!

**Pros**: Free, easy setup, automatic deployments
**Cons**: 500 hours/month limit (bot sleeps after that)

---

## Option 2: Render.com (Free Alternative) 🎨

Render offers free tier with always-on services.

### Steps:

1. **Push Code to GitHub** (same as Railway step 1)

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Set:
     - **Name**: Your bot name
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python bot.py`
   - Add Environment Variables (same as Railway)
   - Click "Create Background Worker"

3. **Monitor**
   - Check logs in Render dashboard
   - Free tier may spin down after inactivity but restarts automatically

**Pros**: Free, reliable, good for small bots
**Cons**: May have cold starts, limited resources

---

## Option 3: PythonAnywhere (Good for Persistent Files) 🐍

PythonAnywhere is great if you want to keep Excel files persistent.

### Steps:

1. **Sign Up**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Create free account

2. **Upload Code**
   - Go to "Files" tab
   - Upload all your project files OR
   - Use "Bash console" to clone from GitHub:
     ```bash
     git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
     cd YOUR_REPO
     ```

3. **Install Dependencies**
   - Open a Bash console
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

4. **Set Environment Variables**
   - Create `.env` file in PythonAnywhere file editor
   - Add all your configuration

5. **Run Bot as Always-On Task**
   - Go to "Tasks" tab
   - Add scheduled task: `python3.10 /home/YOUR_USERNAME/project_major/bot.py`
   - Or use "Always-on task" (paid feature)

**Pros**: Persistent file storage (Excel files saved), easy access
**Cons**: Free tier limited, may need paid plan for 24/7

---

## Option 4: DigitalOcean Droplet (Most Reliable - $6/month) 💧

For production use, a VPS is best.

### Steps:

1. **Create Droplet**
   - Sign up at [DigitalOcean](https://www.digitalocean.com)
   - Create Ubuntu 22.04 Droplet ($6/month)

2. **SSH into Server**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

3. **Setup Server**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python
   apt install python3-pip python3-venv git -y
   
   # Clone your repository
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file
   nano .env
   # (Add your environment variables)
   ```

4. **Run Bot with systemd (Auto-restart)**
   ```bash
   # Create service file
   nano /etc/systemd/system/telegram-bot.service
   ```
   
   Add this content:
   ```ini
   [Unit]
   Description=Telegram Order Bot
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/YOUR_REPO
   Environment="PATH=/root/YOUR_REPO/venv/bin"
   ExecStart=/root/YOUR_REPO/venv/bin/python bot.py
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

5. **Check Logs**
   ```bash
   journalctl -u telegram-bot -f
   ```

**Pros**: Full control, persistent files, reliable 24/7, fast
**Cons**: Costs $6/month, requires some Linux knowledge

---

## Option 5: Your Local Machine (Temporary Testing) 💻

Keep your bot running on your computer - **NOT RECOMMENDED for production**.

### Steps:

1. **Keep Terminal Open**
   ```bash
   python bot.py
   ```

2. **Use `nohup` (Linux/Mac) or Task Scheduler (Windows)**
   
   **Windows Task Scheduler:**
   - Open Task Scheduler
   - Create Basic Task
   - Trigger: "At startup"
   - Action: Start a program
   - Program: `python`
   - Arguments: `d:\College\project_major\bot.py`
   - Working directory: `d:\College\project_major`

**Pros**: Free, instant testing
**Cons**: Requires your computer to be on 24/7, uses your internet

---

## Important Notes 📝

### Before Deploying:

1. **Never commit .env file to GitHub!**
   - The `.gitignore` file I created prevents this
   - Always set environment variables in the hosting platform

2. **Email Configuration**
   - Make sure you have a valid Gmail App Password
   - Test email sending before deploying

3. **Excel Files**
   - Excel files (`orders.xlsx`, `customers.xlsx`) will be created automatically
   - On Railway/Render, files may be lost on redeployment (consider upgrading to a database later)

4. **Test Locally First**
   - Always test your bot locally before deploying
   - Check all commands work

### After Deploying:

1. **Monitor Logs** regularly
2. **Test the bot** by sending commands
3. **Check email notifications** are working
4. **Verify order storage** is functioning

---

## Quick Comparison Table

| Platform | Cost | Ease | Persistent Files | Best For |
|----------|------|------|------------------|----------|
| Railway | Free* | ⭐⭐⭐⭐⭐ | ❌ | Quick deployment |
| Render | Free* | ⭐⭐⭐⭐ | ❌ | Alternative to Railway |
| PythonAnywhere | Free** | ⭐⭐⭐ | ✅ | Keeping Excel files |
| DigitalOcean | $6/mo | ⭐⭐⭐ | ✅ | Production use |
| Local Machine | Free | ⭐⭐⭐⭐⭐ | ✅ | Testing only |

*Limited free tier
**Limited features on free tier

---

## My Recommendation 🌟

**Start with Railway.app** - It's the easiest and fastest way to get your bot online. If you need persistent file storage for Excel files, upgrade to PythonAnywhere (paid) or DigitalOcean.

For a production bot with many users, go with **DigitalOcean** from the start.

---

## Need Help?

- Check deployment logs for errors
- Test environment variables are set correctly
- Ensure `.gitignore` excludes `.env` file
- Verify bot token is valid

Good luck with your deployment! 🚀
