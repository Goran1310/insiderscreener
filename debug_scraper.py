import asyncio
from playwright.async_api import async_playwright

async def debug_table_structure(url):
    """Debug the table structure to understand column alignment"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")
        
        # Wait for table to load
        await page.wait_for_selector('#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table > tbody')
        
        # Debug table structure
        debug_info = await page.evaluate('''() => {
            const table = document.querySelector('#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table');
            
            // Get headers
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => ({
                text: th.textContent.trim(),
                colspan: th.getAttribute('colspan') || '1'
            }));
            
            // Get first row cells
            const firstRow = table.querySelector('tbody tr');
            const cells = Array.from(firstRow.querySelectorAll('td'));
            
            const cellData = cells.map((cell, idx) => {
                // Get only direct text or first 100 chars
                let text = cell.textContent.trim().replace(/\\s+/g, ' ');
                if (text.length > 100) text = text.substring(0, 100) + '...';
                
                return {
                    index: idx,
                    text: text,
                    colspan: cell.getAttribute('colspan') || '1',
                    classes: cell.className
                };
            });
            
            return {
                headers: headers,
                firstRowCells: cellData,
                totalCells: cells.length,
                totalHeaders: headers.length
            };
        }''')
        
        print("\n=== TABLE STRUCTURE DEBUG ===")
        print(f"\nTotal Headers: {debug_info['totalHeaders']}")
        print(f"Total Cells in first row: {debug_info['totalCells']}")
        
        print("\n--- HEADERS ---")
        for i, header in enumerate(debug_info['headers']):
            print(f"Header[{i}]: '{header['text']}' (colspan={header['colspan']})")
        
        print("\n--- FIRST ROW CELLS ---")
        for cell in debug_info['firstRowCells']:
            print(f"\nCell[{cell['index']}]:")
            print(f"  Text: {cell['text']}")
            print(f"  Colspan: {cell['colspan']}")
            print(f"  Classes: {cell['classes']}")
        
        await browser.close()

async def main():
    url = "https://www.insiderscreener.com/en/company/afry-ab"
    await debug_table_structure(url)

if __name__ == "__main__":
    asyncio.run(main())
