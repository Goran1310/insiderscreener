import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
from pathlib import Path
import hashlib

class InsiderDataManager:
    """Manages insider trading data with historical tracking and change detection"""
    
    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)
        self.current_dir = self.base_dir / "current"
        self.history_dir = self.base_dir / "history"
        self.changes_dir = self.base_dir / "changes"
        
        # Create directories
        self.current_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.changes_dir.mkdir(parents=True, exist_ok=True)
    
    def _transaction_hash(self, transaction):
        """Create a unique hash for a transaction"""
        # Use key fields to create a unique identifier
        key = f"{transaction['notification_date']}_{transaction['transaction_date']}_{transaction['insider_name']}_{transaction['number_of_shares']}_{transaction['value']}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def detect_changes(self, old_data, new_data):
        """Detect changes between old and new data"""
        if not old_data:
            return {
                'has_changes': True,
                'new_transactions': len(new_data['transactions']),
                'removed_transactions': 0,
                'modified_transactions': 0,
                'details': {'type': 'initial_load', 'message': 'First time scraping this company'}
            }
        
        old_txns = {self._transaction_hash(t): t for t in old_data['transactions']}
        new_txns = {self._transaction_hash(t): t for t in new_data['transactions']}
        
        # Find new, removed, and common transactions
        old_hashes = set(old_txns.keys())
        new_hashes = set(new_txns.keys())
        
        new_transaction_hashes = new_hashes - old_hashes
        removed_transaction_hashes = old_hashes - new_hashes
        
        # Company metrics changes
        metrics_changed = (
            old_data['company_info'].get('value_bought') != new_data['company_info'].get('value_bought') or
            old_data['company_info'].get('value_sold') != new_data['company_info'].get('value_sold') or
            old_data['company_info'].get('net_insiders_buying') != new_data['company_info'].get('net_insiders_buying') or
            old_data['company_info'].get('trades_count') != new_data['company_info'].get('trades_count')
        )
        
        has_changes = len(new_transaction_hashes) > 0 or len(removed_transaction_hashes) > 0 or metrics_changed
        
        changes = {
            'has_changes': has_changes,
            'new_transactions': len(new_transaction_hashes),
            'removed_transactions': len(removed_transaction_hashes),
            'metrics_changed': metrics_changed,
            'details': {
                'new_transactions_list': [new_txns[h] for h in new_transaction_hashes],
                'removed_transactions_list': [old_txns[h] for h in removed_transaction_hashes],
                'old_metrics': old_data['company_info'],
                'new_metrics': new_data['company_info']
            }
        }
        
        return changes
    
    def save_data(self, company_slug, data, changes):
        """Save data with historical tracking"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Save to current directory
        current_file = self.current_dir / f"{company_slug}.json"
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save to history only if there are changes
        if changes['has_changes']:
            company_history_dir = self.history_dir / company_slug
            company_history_dir.mkdir(exist_ok=True)
            
            history_file = company_history_dir / f"{timestamp}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save change log
            change_log_file = self.changes_dir / f"{company_slug}_changes.json"
            
            # Load existing change log or create new
            if change_log_file.exists():
                with open(change_log_file, 'r', encoding='utf-8') as f:
                    change_log = json.load(f)
            else:
                change_log = {'company': company_slug, 'changes': []}
            
            # Add new change entry
            change_entry = {
                'timestamp': timestamp,
                'scraped_at': data['scraped_at'],
                'new_transactions': changes['new_transactions'],
                'removed_transactions': changes['removed_transactions'],
                'metrics_changed': changes.get('metrics_changed', False),
                'details': changes['details']
            }
            change_log['changes'].append(change_entry)
            
            # Keep only last 100 changes
            change_log['changes'] = change_log['changes'][-100:]
            
            with open(change_log_file, 'w', encoding='utf-8') as f:
                json.dump(change_log, f, indent=2, ensure_ascii=False)
        
        return current_file
    
    def load_current_data(self, company_slug):
        """Load current data for a company"""
        current_file = self.current_dir / f"{company_slug}.json"
        if current_file.exists():
            with open(current_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

async def scrape_insider_data(url):
    """Scrape insider trading data from insiderscreener.com"""
    
    async with async_playwright() as p:
        # Run headless for production/scheduled runs
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Wait for table to load
        await page.wait_for_selector('#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table > tbody')
        
        # Extract company information
        company_name = await page.locator('h1').text_content()
        print(f"Scraping data for: {company_name}")
        
        # Extract table data with proper column alignment
        transactions = await page.evaluate('''() => {
            const table = document.querySelector('#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table');
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            const data = [];
            
            rows.forEach((row, idx) => {
                const cells = row.querySelectorAll('td');
                
                if (cells.length >= 8) {
                    // Extract insider name and position from cell 3
                    const insiderCell = cells[3];
                    const insiderLink = insiderCell.querySelector('a[href*="/en/insider/"]');
                    const positionPara = insiderCell.querySelector('p small');
                    const roleBadge = insiderCell.querySelector('span.badge.badge-light');
                    
                    // Get additional info
                    const smallTags = insiderCell.querySelectorAll('small');
                    let additionalInfo = '';
                    smallTags.forEach(small => {
                        if (!small.closest('p')) {
                            additionalInfo = small.textContent.trim();
                        }
                    });
                    
                    // Cell[4] contains combined data for mobile (skip it)
                    // Cell[5] = number of shares (desktop)
                    // Cell[6] = price (desktop)
                    // Cell[7] = value (desktop)
                    
                    // Extract numeric values for validation
                    const shares = cells[5].textContent.trim();
                    const price = cells[6].textContent.trim();
                    const value = cells[7].textContent.trim();
                    
                    // Calculate actual price from value and shares
                    let calculatedPrice = '';
                    try {
                        const sharesNum = parseFloat(shares.replace(/,/g, ''));
                        // Handle both SEK and USD values
                        const valueNum = parseFloat(value.replace(/SEK|USD|EUR|,/g, '').trim());
                        if (sharesNum > 0 && valueNum > 0) {
                            calculatedPrice = (valueNum / sharesNum).toFixed(2);
                        }
                    } catch (e) {}
                    
                    const transaction = {
                        notification_date: cells[0].textContent.trim(),
                        transaction_date: cells[1].textContent.trim(),
                        transaction_type: cells[2].textContent.trim().split('\\n').pop().trim(),
                        insider_name: insiderLink ? insiderLink.textContent.trim() : '',
                        insider_position: positionPara ? positionPara.textContent.trim() : '',
                        insider_role: roleBadge ? roleBadge.textContent.trim() : '',
                        additional_info: additionalInfo,
                        number_of_shares: shares,
                        price: price,
                        price_calculated: calculatedPrice,
                        value: value
                    };
                    data.push(transaction);
                }
            });
            
            return data;
        }''')
        
        # Extract additional company metrics
        company_info = await page.evaluate('''() => {
            const getMetricValue = (text) => {
                const element = Array.from(document.querySelectorAll('h6')).find(el => el.textContent.includes(text));
                return element && element.parentElement ? element.parentElement.querySelector('h5')?.textContent.trim() : '';
            };
            
            return {
                company_name: document.querySelector('h1')?.textContent.trim() || '',
                value_bought: getMetricValue('Value bought'),
                value_sold: getMetricValue('Value sold'),
                net_insiders_buying: getMetricValue('Net insiders buying'),
                trades_count: getMetricValue('Trades'),
                insider_activity: getMetricValue('Insider activity')
            };
        }''')
        
        await browser.close()
        
        return {
            'scraped_at': datetime.now().isoformat(),
            'url': url,
            'company_info': company_info,
            'transactions': transactions,
            'total_transactions': len(transactions)
        }

async def main():
    # List of all companies to track
    companies = [
        "https://www.insiderscreener.com/en/company/afry-ab",
        "https://www.insiderscreener.com/en/company/academedia-ab",
        "https://www.insiderscreener.com/en/company/note-ab-publ",
        "https://www.insiderscreener.com/en/company/knowit-ab-publ",
        "https://www.insiderscreener.com/en/company/byggmax-group-ab",
        "https://www.insiderscreener.com/en/company/coor-service-management-holding-ab",
        "https://www.insiderscreener.com/en/company/bravida-holding-ab",
        "https://www.insiderscreener.com/en/company/essity-ab-publ",
        "https://www.insiderscreener.com/en/company/scandic-hotels-group-ab",
        "https://www.insiderscreener.com/en/company/rvrc-holding-ab",
        "https://www.insiderscreener.com/en/company/eqt-ab",
        "https://www.insiderscreener.com/en/company/inwido-ab-publ",
        "https://www.insiderscreener.com/en/company/vbg-group-ab-publ",
    ]
    
    # Initialize data manager
    manager = InsiderDataManager()
    
    print(f"\n{'='*60}")
    print(f"INSIDER SCREENER - TRACKING {len(companies)} COMPANIES")
    print(f"{'='*60}\n")
    
    total_new_transactions = 0
    companies_with_changes = []
    
    for idx, url in enumerate(companies, 1):
        company_slug = url.rstrip('/').split('/')[-1]
        
        print(f"\n[{idx}/{len(companies)}] Processing: {company_slug}")
        print("-" * 60)
        
        # Load previous data
        old_data = manager.load_current_data(company_slug)
        if old_data:
            print(f"✓ Loaded previous data from {old_data['scraped_at']}")
        else:
            print("✓ No previous data found - first scrape")
        
        # Scrape new data
        try:
            new_data = await scrape_insider_data(url)
            
            # Detect changes
            changes = manager.detect_changes(old_data, new_data)
            
            if changes['has_changes']:
                print(f"\n📊 CHANGES DETECTED")
                
                if changes['new_transactions'] > 0:
                    print(f"   ✨ New transactions: {changes['new_transactions']}")
                    total_new_transactions += changes['new_transactions']
                    if 'new_transactions_list' in changes['details']:
                        for txn in changes['details']['new_transactions_list'][:2]:
                            print(f"      • {txn['transaction_date']} - {txn['insider_name']}: {txn['transaction_type']}")
                
                if changes['removed_transactions'] > 0:
                    print(f"   🗑️  Removed transactions: {changes['removed_transactions']}")
                
                if changes.get('metrics_changed'):
                    print(f"   📈 Company metrics changed")
                
                companies_with_changes.append(company_slug)
                
                # Save data with history
                saved_file = manager.save_data(company_slug, new_data, changes)
                print(f"   ✓ Data saved with historical snapshot")
                
            else:
                print(f"✓ No changes detected - data is up to date")
                # Still update current file with new timestamp
                saved_file = manager.save_data(company_slug, new_data, changes)
                print(f"✓ Current data refreshed")
            
            print(f"\nCompany: {new_data['company_info']['company_name'].strip()}")
            print(f"Total Transactions: {new_data['total_transactions']}")
            
        except Exception as e:
            print(f"❌ Error scraping {company_slug}: {str(e)}")
            continue
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Companies tracked: {len(companies)}")
    print(f"Companies with changes: {len(companies_with_changes)}")
    print(f"Total new transactions: {total_new_transactions}")
    if companies_with_changes:
        print(f"\nCompanies updated:")
        for company in companies_with_changes:
            print(f"  • {company}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
