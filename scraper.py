import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def scrape_insider_data(url):
    """Scrape insider trading data from insiderscreener.com"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
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
            
            // Get header columns to verify structure
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
            console.log('Headers:', headers);
            
            rows.forEach((row, idx) => {
                const cells = row.querySelectorAll('td');
                
                // Debug first row
                if (idx === 0) {
                    console.log('Number of cells in row:', cells.length);
                    cells.forEach((cell, i) => {
                        const text = cell.textContent.trim().replace(/\\s+/g, ' ').substring(0, 60);
                        console.log(`Cell[${i}]: ${text}`);
                    });
                }
                
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
                    const transaction = {
                        notification_date: cells[0].textContent.trim(),
                        transaction_date: cells[1].textContent.trim(),
                        transaction_type: cells[2].textContent.trim().split('\\n').pop().trim(),
                        insider_name: insiderLink ? insiderLink.textContent.trim() : '',
                        insider_position: positionPara ? positionPara.textContent.trim() : '',
                        insider_role: roleBadge ? roleBadge.textContent.trim() : '',
                        additional_info: additionalInfo,
                        number_of_shares: cells[5].textContent.trim(),
                        price: cells[6].textContent.trim(),
                        value: cells[7].textContent.trim()
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
    url = "https://www.insiderscreener.com/en/company/afry-ab"
    
    print("Starting scraper...")
    data = await scrape_insider_data(url)
    
    # Extract company slug from URL for filename
    company_slug = url.rstrip('/').split('/')[-1]
    output_file = f'{company_slug}.json'
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Scraped {data['total_transactions']} transactions")
    print(f"✓ Data saved to {output_file}")
    print(f"\nCompany: {data['company_info']['company_name']}")
    print(f"Value Bought: {data['company_info']['value_bought']}")
    print(f"Value Sold: {data['company_info']['value_sold']}")
    print(f"Net Insiders Buying: {data['company_info']['net_insiders_buying']}")
    print(f"Total Trades: {data['company_info']['trades_count']}")

if __name__ == "__main__":
    asyncio.run(main())
