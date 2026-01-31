# 🚀 Quick Start Guide

Get HR up and running in 5 minutes!

## Step 1: Get Your Credentials

### 1.1 Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the **bot token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 1.2 Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

## Step 2: Setup Database

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE .hr_db;"
sudo -u postgres psql -c "CREATE USER .hr_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE .hr_db TO .hr_user;"
```

## Step 3: Install Application

```bash
# Clone repository
git clone https://github.com/yourusername/.HR-Telegram-Bot.git
cd .HR-Telegram-Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Fill in:**
```env
DB_USER=.hr_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=.hr_db

TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 5: Initialize Database

```bash
# Create tables
python scripts/setup_database.py

# Generate sample data (optional)
python scripts/generate_sample_data.py
```

## Step 6: Run the Bot

```bash
# Start bot
python src/bot.py
```

You should see:
```
🤖 .HR Telegram Bot Started
✅ Bot: @YourBotName
🧠 Architecture: Agent-based
🔧 LLM: Google Gemini 2.5 Flash
💾 Database: PostgreSQL
⏳ Waiting for messages...
```

## Step 7: Test the Bot

1. Open Telegram and search for your bot
2. Send `/start`
3. Send your **Employee ID** (if you generated sample data, IDs are 1-25)
4. Try: `"What's my leave balance?"`

## 🎉 That's it!

Your bot is now running!

### Next Steps

- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the system
- Check [DEPLOYMENT.md](docs/DEPLOYMENT.md) for production deployment
- Explore [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for database details

### Common Issues

**Database connection error?**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U .hr_user -h localhost -d .hr_db
```

**Bot not responding?**
- Check bot token is correct in `.env`
- Verify Gemini API key is valid
- Check firewall allows outbound HTTPS

**Import errors?**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Need Help?

- Check the [full README](README.md)
- Review [troubleshooting guide](docs/DEPLOYMENT.md#troubleshooting)
- Open an issue on GitHub

---

