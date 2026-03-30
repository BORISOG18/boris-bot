# 🤖 BORIS OG STORE — Telegram Invoice Bot

## 📁 Files
```
boris_bot/
├── bot.py                  ← Main bot
├── invoice_generator.py    ← PDF generator
├── db.py                   ← Customer database
├── requirements.txt        ← Dependencies
├── boris_logo.jpeg         ← Your store logo ⬅ copy this here
└── customers.json          ← Auto-created when first customer saved
```

---

## 🚀 Setup on Your Laptop (One Time)

### Step 1 — Install Python
Download from https://python.org (3.10 or higher)

### Step 2 — Open Terminal / Command Prompt
```bash
cd path/to/boris_bot
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Add your Bot Token
Open `bot.py` and replace this line:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```
with your new token from @BotFather:
```python
BOT_TOKEN = "12345678:ABCdef..."
```

### Step 5 — Copy your logo
Make sure `boris_logo.jpeg` is inside the `boris_bot/` folder

### Step 6 — Run the bot
```bash
python bot.py
```
You should see: `🤖 BORIS OG STORE Bot is running!`

---

## 📱 Using on iPhone (Telegram)

Open Telegram → search your bot → tap **Start**

### Bot Commands:
| Button | Action |
|--------|--------|
| 📄 New Invoice | Create invoice step by step |
| 📋 All Customers | See last 15 customers |
| 🔍 Find Customer | Search by name or ID |
| ✅ Mark Paid | Update pending → paid |
| /cancel | Cancel current action |

### New Invoice Flow:
1. Customer Name
2. Customer ID
3. Item Name
4. Amount (RS)
5. Payment Status (Paid / Pending)
6. Delivery Date
7. Delivery Time
8. Car Image (or /skip)
→ Bot sends PDF invoice instantly!

---

## ⚠️ Keep Bot Running
- Bot only works while your laptop is ON and `python bot.py` is running
- To keep it running 24/7, consider Railway.app or Render.com (free hosting)

---

## 🔐 Security
- NEVER share your bot token publicly
- If leaked, revoke it immediately via @BotFather → /mybots → API Token → Revoke
