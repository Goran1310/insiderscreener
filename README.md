# Insider Screener Web Scraper

**Production-ready insider trading tracker with historical data management and change detection.**

## 🎯 Project Overview

This project scrapes insider trading data from [insiderscreener.com](https://www.insiderscreener.com) for multiple Swedish companies, automatically tracking changes over time and maintaining a complete historical record.

### Key Features
- ✅ Multi-company tracking (13 companies)
- ✅ Smart change detection (only saves when data changes)
- ✅ Historical snapshots with timestamps
- ✅ Detailed change logs with transaction diffs
- ✅ Price validation (calculated vs displayed)
- ✅ Multi-currency support (SEK, USD, EUR)
- ✅ Headless browser operation
- ✅ Production-ready for scheduled runs

## 📁 Project Structure

```
insiderscreener/
├── data/
│   ├── current/              # Latest scraped data (always updated)
│   │   ├── afry-ab.json
│   │   ├── academedia-ab.json
│   │   └── ...
│   ├── history/              # Timestamped snapshots (only when changes detected)
│   │   ├── afry-ab/
│   │   │   ├── 2025-12-25_17-33-57.json
│   │   │   └── ...
│   │   └── ...
│   └── changes/              # Change logs with detailed diffs
│       ├── afry-ab_changes.json
│       └── ...
├── scraper_with_history.py   # Main production scraper
├── scraper.py                # Basic scraper (legacy)
├── debug_scraper.py          # Table structure debugger
└── requirements.txt
```

## 🚀 Setup

1. **Install dependencies:**
```bash
pip install playwright
playwright install chromium
```

2. **Run the scraper:**
```bash
python scraper_with_history.py
```

## 📊 Tracked Companies

1. Afry AB (AFRY)
2. AcadeMedia AB (ACAD)
3. Note AB (publ) (NOTE)
4. Knowit AB (publ) (KNOW)
5. Byggmax Group AB (BMAX)
6. Coor Service Management Holding AB (COOR)
7. Bravida Holding AB (BRAV)
8. Essity AB (publ) (ESSITY-B)
9. Scandic Hotels Group AB (SHOT)
10. RVRC Holding AB (RVRC)
11. EQT AB (EQT)
12. Inwido AB (publ) (INWI)
13. VBG Group AB (publ) (VBG-B)

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

## 🛠️ Future Development Guidelines

### Adding New Companies
1. Add URL to `companies` list in [scraper_with_history.py](scraper_with_history.py#L239)
2. Run scraper to initialize tracking
3. Commit and push to GitHub

### Modifying Table Scraping
1. Use `debug_scraper.py` to inspect table structure first
2. Update cell indices in the `page.evaluate()` section
3. Test with a single company before full run
4. Validate data structure in output JSON

### Scheduling Automated Runs
**Windows Task Scheduler:**
```powershell
# Create scheduled task (daily at 9 AM)
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\scraper_with_history.py" -WorkingDirectory "C:\path\to\insiderscreener"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "InsiderScreener" -Description "Daily insider trading scraper"
```

**Linux Cron:**
```bash
# Add to crontab (daily at 9 AM)
0 9 * * * cd /path/to/insiderscreener && python scraper_with_history.py >> scraper.log 2>&1
```

### Error Handling
The scraper includes try-catch for individual companies. Failed companies are logged but don't stop the entire run.

### Performance Optimization
- Headless mode enabled (faster)
- Sequential processing (avoids rate limiting)
- ~4-5 seconds per company
- Total runtime: ~60 seconds for 13 companies

## 🐛 Known Issues

1. **Price Discrepancies:** insiderscreener.com displays incorrect prices for some transactions. Use `price_calculated` for accurate values.
2. **Rate Limiting:** If scraping fails, add delays between companies using `await asyncio.sleep(2)`.

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
**Version:** 1.0  
**Maintained by:** Goran Lovincic
