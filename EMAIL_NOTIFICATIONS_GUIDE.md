# Email Notification Quick Start Guide

## ✅ Setup Complete!

Your Insider Screener now automatically sends email alerts when new insider trading transactions are detected.

## 📧 How It Works

When you run the scraper:
```bash
python main.py --all
```

**If new transactions are detected:**
1. ✅ Scraper detects new insider trading transactions
2. 📧 **Email sent IMMEDIATELY** with only the new transactions
3. 📊 Email includes:
   - Company name and link
   - Transaction type (Purchase/Sale)
   - Insider name, position, role
   - Number of shares
   - Price and total value
   - Transaction dates

**Example Email:**
```
Subject: 🚨 New Insider Trading: AFRY AB (2 transactions)

New Transactions (2):

Transaction #1 📈
Type: Purchase
Notification Date: 2025-12-25
Insider: John Doe (CEO)
Shares: 50,000
Value: SEK 6,275,000

Transaction #2 📉
Type: Sale
Notification Date: 2025-12-25
Insider: Jane Smith (CFO)
Shares: 25,000
Value: SEK 3,000,000
```

## 🔧 Configuration

Your `.env` file:
```env
EMAIL_USER=lovincic@gmail.com
EMAIL_PASS=gnevdeziyxmuhnfj
RECIPIENT_EMAIL=lovincic@gmail.com
SEND_NOTIFICATIONS=true
SEND_SUMMARY=false
```

### Settings:
- `SEND_NOTIFICATIONS=true` → Send email for each company with new transactions
- `SEND_SUMMARY=true` → Also send summary email at the end (optional)

## 🧪 Test Before Running

Test the email system:
```bash
python test_notifications.py
```

This sends a test email with sample transactions to verify everything works.

## 🚀 Usage Examples

### Check All Companies (with notifications)
```bash
python main.py --all
```
→ Emails sent for each company with new transactions

### Check Specific Companies
```bash
python main.py --companies afry-ab bouvet-asa
```
→ Only checks these 2 companies, sends email if new transactions found

### Check Without Emails (temporary)
Edit `.env` and set `SEND_NOTIFICATIONS=false`, or temporarily disable in config.py

## 📊 Scheduling (Recommended)

### Windows Task Scheduler
```powershell
# Run daily at 9 AM
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\goran.lovincic\source\repos\insiderscreener\main.py --all" -WorkingDirectory "C:\Users\goran.lovincic\source\repos\insiderscreener"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "InsiderScreenerMonitor" -Description "Daily insider trading monitor with email alerts"
```

### Result
- ✅ Scraper runs automatically every day at 9 AM
- 📧 You receive email alerts whenever new insider trades are detected
- 📊 No emails sent if no new transactions

## 🎯 What Gets Emailed

✅ **ONLY NEW TRANSACTIONS** - Not all data, just the new rows detected since last scrape

❌ **NO EMAIL SENT WHEN:**
- No changes detected
- Data unchanged from previous scrape
- All transactions already seen before

## 📝 Log Files

Check activity:
```bash
# View scraper log
type scraper.log

# Recent entries
Get-Content scraper.log -Tail 50
```

## 🔐 Security

- Your `.env` file is excluded from Git (in `.gitignore`)
- Never commit email credentials to repository
- Gmail app password is separate from your main password

## ✅ You're All Set!

The system is configured and tested. When you run:
```bash
python main.py --all
```

You'll automatically receive email alerts for any new insider trading transactions! 🎉
