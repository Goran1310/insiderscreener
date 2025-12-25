import asyncio
from playwright.async_api import async_playwright

async def debug_academedia_table():
    """Debug the academedia table structure"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "https://www.insiderscreener.com/en/company/academedia-ab"
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Wait for table to load
        await page.wait_for_selector('#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table > tbody')
        
        # Debug specific problematic row (3rd row - index 2)
        debug_info = await page.evaluate('''() => {
            const table = document.querySelector('#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table');
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            
            // Get row 2 (3rd transaction - Purchase Marie-Louise Sörman 6,877 shares)
            const row = rows[2];
            const cells = Array.from(row.querySelectorAll('td'));
            
            const cellData = cells.map((cell, idx) => {
                let text = cell.textContent.trim().replace(/\\s+/g, ' ');
                if (text.length > 150) text = text.substring(0, 150) + '...';
                
                return {
                    index: idx,
                    text: text,
                    classes: cell.className
                };
            });
            
            // Also get the calculation
            const shares = cells[5] ? cells[5].textContent.trim() : '';
            const price = cells[6] ? cells[6].textContent.trim() : '';
            const value = cells[7] ? cells[7].textContent.trim() : '';
            
            return {
                totalCells: cells.length,
                cellData: cellData,
                extracted: {
                    shares: shares,
                    price: price,
                    value: value
                }
            };
        }''')
        
        print("\n=== ACADEMEDIA ROW 3 DEBUG (Marie-Louise Sörman Purchase 6,877) ===")
        print(f"Total Cells: {debug_info['totalCells']}")
        
        print("\n--- ALL CELLS ---")
        for cell in debug_info['cellData']:
            print(f"\nCell[{cell['index']}]:")
            print(f"  Text: {cell['text']}")
            print(f"  Classes: {cell['classes']}")
        
        print("\n--- EXTRACTED VALUES ---")
        print(f"Shares (Cell[5]): {debug_info['extracted']['shares']}")
        print(f"Price (Cell[6]): {debug_info['extracted']['price']}")
        print(f"Value (Cell[7]): {debug_info['extracted']['value']}")
        
        # Calculate what price should be
        try:
            shares_num = float(debug_info['extracted']['shares'].replace(',', ''))
            value_text = debug_info['extracted']['value'].replace('SEK', '').replace(',', '').strip()
            value_num = float(value_text)
            calculated_price = value_num / shares_num
            print(f"\n--- CALCULATION ---")
            print(f"Calculated price: {calculated_price:.2f} SEK per share")
            print(f"Scraped price: {debug_info['extracted']['price']}")
            print(f"Match: {abs(float(debug_info['extracted']['price']) - calculated_price) < 0.01}")
        except:
            print("Could not calculate price")
        
        await browser.close()

asyncio.run(debug_academedia_table())
