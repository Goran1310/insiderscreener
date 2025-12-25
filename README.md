# Insider Screener Web Scraper

**Production-ready insider trading tracker with historical data management and change detection.**

## 🎯 Project Overview

This project scrapes insider trading data from [insiderscreener.com](https://www.insiderscreener.com) for multiple Swedish companies, automatically tracking changes over time and maintaining a complete historical record.

### Key Features
- ✅ Multi-company tracking (13 companies)
- ✅ Smart change detection (only saves when data changes)
- ✅ **Email notifications for new transactions**
- ✅ Historical snapshots with timestamps
- ✅ Detailed change logs with transaction diffs
- ✅ Price validation (calculated vs displayed)
- ✅ Multi-currency support (SEK, USD, EUR)
- ✅ Professional logging framework
- ✅ Retry logic with exponential backoff
- ✅ CLI interface for selective scraping
- ✅ Modular architecture
- ✅ Headless browser operation
- ✅ Production-ready for scheduled runs

## 📁 Project Structure

```
insiderscreener/
├── data/                     # Data storage
│   ├── current/              # Latest scraped data (always updated)
│   ├── history/              # Timestamped snapshots (only when changes)
│   └── changes/              # Change logs with detailed diffs
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── logging_config.py     # Logging setup
│   └── retry.py              # Retry logic with exponential backoff
├── config.py                 # Configuration settings
├── data_manager.py           # Data persistence and change detection
├── scraper.py                # Core scraping logic
├── main.py                   # CLI entry point
├── scraper_with_history.py   # Legacy monolithic version (archived)
├── debug_scraper.py          # Table structure debugger
├── requirements.txt          # Dependencies
└── README.md
```

## 🚀 Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Configure email notifications (optional):**

Create a `.env` file in the project root:
```env
# Email Configuration (Gmail)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password
RECIPIENT_EMAIL=recipient@gmail.com

# Notification Settings
SEND_NOTIFICATIONS=true
SEND_SUMMARY=false
```

**Gmail App Password Setup:**
- Go to https://myaccount.google.com/apppasswords
- Generate an app password for "Mail"
- Use this password (not your regular Gmail password)

3. **Run the scraper:**

```bash
# Scrape all companies
python main.py --all

# Scrape specific companies
python main.py --companies afry-ab bouvet-asa

# List all tracked companies
python main.py --list

# Run with visible browser (for debugging)
python main.py --all --no-headless
```

## 📊 Tracked Companies

1. AFRY AB
2. AcadeMedia AB
3. Akelius Residential Property AB
4. Byggmax Group AB
5. Bouvet ASA
6. Bravida Holding AB
7. Essity AB
8. Scandic Hotels Group AB
9. RVRC Holding AB
10. EQT AB
11. Inwido AB
12. VBG Group AB

*Full list with URLs maintained in [config.py](config.py)*

## 🔧 Configuration

All configuration is centralized in [config.py](config.py):

### Company Management
Add or remove companies by editing the `COMPANIES` list:
```python
COMPANIES = [
    {
        "slug": "afry-ab",
        "name": "AFRY AB",
        "url": "https://www.insiderscreener.com/en/company/afry-ab"
    },
    # Add more companies...
]
```

### Scraper Settings
```python
SCRAPER_CONFIG = {
    "headless": True,               # Run browser in headless mode
    "timeout": 30000,               # Page load timeout (ms)
    "retry_attempts": 3,            # Number of retry attempts
    "retry_delay_base": 2,          # Exponential backoff base
}
```

### Logging Settings
```python
LOGGING_CONFIG = {
    "level": "INFO",                # Log level (DEBUG, INFO, WARNING, ERROR)
    "log_file": "scraper.log",      # Log file name
    "max_bytes": 10 * 1024 * 1024,  # 10MB max log size
    "backup_count": 5,              # Keep 5 backup log files
}
```

## 📈 Data Structure

Each transaction contains:
```json
{
  "notification_date": "2025-12-18",
  "transaction_date": "2025-12-18",
  "transaction_type": "Purchase/Sale",
  "insider_name": "John Doe",
  "insider_position": "CEO",
  "insider_role": "Officer",
  "additional_info": "Through affiliated company",
  "number_of_shares": "28,676",
  "price": "33.09",
  "price_calculated": "33.09",  // Validated price (value/shares)
  "value": "SEK 3,949,379"
}
```

## 🔍 Technical Details

### Table Structure
The scraper handles insiderscreener.com's responsive table with 9 columns:
- Cell[0]: Notification date
- Cell[1]: Transaction date
- Cell[2]: Transaction type
- Cell[3]: Insider info
- Cell[4]: Mobile-only combined data (skipped)
- Cell[5]: Number of shares (desktop)
- Cell[6]: Price (desktop)
- Cell[7]: Value (desktop)
- Cell[8]: Details

### Change Detection
Uses MD5 hashing of key transaction fields:
- Notification date
- Transaction date
- Insider name
- Number of shares
- Value

### Price Validation
`price_calculated` field shows mathematically correct price (value ÷ shares). Discrepancies indicate data quality issues on insiderscreener.com.

## 🔄 Backup & Version Control

**GitHub Repository:** https://github.com/Goran1310/insiderscreener

**⚠️ IMPORTANT:** Push to GitHub frequently as backup.

```bash
# Initialize (first time only)
git init
git remote add origin https://github.com/Goran1310/insiderscreener.git

# Regular backup workflow
git add .
git commit -m "Update: scraped data $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin main
```

**Recommended backup schedule:**
- After adding new companies
- After major code changes
- Weekly data snapshots
- Before making structural changes

## 🛠️ Architecture

### Module Overview

#### `config.py`
Central configuration for companies, scraper settings, logging, and data management.

#### `scraper.py`
Core scraping functionality:
- Playwright-based web scraping
- Table data extraction
- Company metrics collection
- Automatic retry on failure

#### `data_manager.py`
Data persistence layer:
- JSON file management
- Change detection using MD5 hashing
- Historical snapshots
- Change log maintenance

#### `main.py`
CLI entry point:
- Argument parsing
- Company selection logic
- Progress reporting
- Summary generation
- **Email notification triggering**

#### `notifications.py`
Email notification service:
- Gmail SMTP integration
- HTML email formatting
- New transaction alerts (only new rows)
- Optional summary emails

#### `utils/`
Helper utilities:
- `logging_config.py`: Structured logging setup
- `retry.py`: Exponential backoff retry decorator

### Error Handling

The scraper implements robust error handling:
- **Retry Logic**: Failed requests automatically retry 3 times with exponential backoff
- **Per-Company Isolation**: One company failing doesn't stop others
- **Detailed Logging**: All errors logged to `scraper.log` with full context
- **Graceful Degradation**: Summary shows which companies succeeded/failed

## 🛠️ Future Development Guidelines

### Adding New Companies
1. Add company entry to `COMPANIES` list in [config.py](config.py)
2. Run scraper: `python main.py --companies new-company-slug`
3. Verify data in `data/current/new-company-slug.json`
4. Commit and push to GitHub

### Modifying Table Scraping
1. Use `debug_scraper.py` to inspect table structure first
2. Update extraction logic in [scraper.py](scraper.py) `_extract_transactions()` function
3. Test with a single company: `python main.py --companies afry-ab --no-headless`
4. Validate data structure in output JSON

### Scheduling Automated Runs
**Windows Task Scheduler:**
```powershell
# Create scheduled task (daily at 9 AM)
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\main.py --all" -WorkingDirectory "C:\path\to\insiderscreener"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "InsiderScreener" -Description "Daily insider trading scraper"
```

**Linux Cron:**
```bash
# Add to crontab (daily at 9 AM)
0 9 * * * cd /path/to/insiderscreener && python main.py --all >> scraper.log 2>&1
```

### Error Handling
The scraper includes comprehensive error handling:
- Individual company failures don't stop the entire run
- Failed companies are logged with error details
- Retry logic with exponential backoff for transient failures
- All errors logged to `scraper.log` for debugging

### Performance Optimization
- Headless mode enabled by default (faster)
- Sequential processing (avoids rate limiting)
- Configurable retry delays
- ~4-5 seconds per company
- Total runtime: ~60 seconds for 13 companies

## 🐛 Known Issues

1. **Price Discrepancies:** insiderscreener.com displays incorrect prices for some transactions. Use `price_calculated` for accurate values.
2. **Rate Limiting:** If scraping fails consistently, increase delays in [config.py](config.py) `SCRAPER_CONFIG["retry_delay_base"]`.

## 💡 Usage Examples

### Scrape All Companies
```bash
python main.py --all
```

### Scrape Specific Companies
```bash
python main.py --companies afry-ab bouvet-asa byggmax-group-ab
```

### List Available Companies
```bash
python main.py --list
```

### Debug Mode (Visible Browser)
```bash
python main.py --companies afry-ab --no-headless
```

### View Logs
```bash
# Windows
type scraper.log

# Linux/Mac
tail -f scraper.log
```

### Test Email Notifications
```bash
# Test email configuration
python test_notifications.py

# This will send a test email with sample transactions
```

### Email Notification Behavior

When **new insider trading transactions** are detected:
- ✅ **Instant email alert** sent to your configured email
- 📧 **Only new transactions** included (not all data)
- 🎨 **Formatted HTML email** with transaction details:
  - Transaction type (Purchase/Sale) with color coding
  - Insider name, position, and role
  - Number of shares and value
  - Price (displayed and calculated)
  - Direct link to company page

**No emails sent** when:
- ❌ No new transactions detected
- ❌ Data unchanged from previous scrape
- ❌ Notifications disabled in `.env`

### Disable Notifications
Edit `.env`:
```env
SEND_NOTIFICATIONS=false
```

## 📝 Data Analysis Tips

### Find Recent Insider Buying
```python
import json
from pathlib import Path

for file in Path('data/current').glob('*.json'):
    with open(file) as f:
        data = json.load(f)
    
    purchases = [t for t in data['transactions'] if t['transaction_type'] == 'Purchase']
    if purchases:
        print(f"{data['company_info']['company_name']}: {len(purchases)} purchases")
```

### Detect Price Anomalies
```python
for transaction in data['transactions']:
    if transaction['price_calculated']:
        displayed = float(transaction['price'])
        calculated = float(transaction['price_calculated'])
        diff_pct = abs(displayed - calculated) / calculated * 100
        
        if diff_pct > 10:
            print(f"Price anomaly: {transaction['insider_name']} - {diff_pct:.1f}% difference")
```

## 📞 Maintenance

- **Update Playwright:** `pip install --upgrade playwright && playwright install chromium`
- **Check GitHub for changes:** Regularly pull updates
- **Review change logs:** Monitor `data/changes/` for unusual activity
- **Validate data:** Spot-check recent transactions on insiderscreener.com

## 🔐 Security Notes

- No API keys required (public data)
- Respects robots.txt
- Sequential requests (no aggressive scraping)
- User-agent: Default Playwright browser

---

**Last Updated:** December 25, 2025  
**Version:** 2.0 (Refactored Architecture)  
**Maintained by:** Goran Lovincic

## 📝 Changelog

### Version 2.0 (December 25, 2025)
- ✨ Modular architecture with separate modules
- ✨ Professional logging framework
- ✨ Retry logic with exponential backoff
- ✨ CLI interface with argparse
- ✨ Centralized configuration
- ✨ **Email notifications for new transactions**
- ✨ Type hints and documentation
- 🗑️ Removed legacy files (scraper.py monolithic, debug_academedia.py)

### Version 1.0 (December 24, 2025)
- ✅ Initial release with monolithic scraper
- ✅ Historical tracking and change detection
- ✅ 13 companies tracked
- ✅ GitHub integration
