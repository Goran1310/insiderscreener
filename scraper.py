"""
Core web scraping functionality for InsiderScreener
"""

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from typing import Dict, Any
from config import SCRAPER_CONFIG
from utils.logging_config import get_logger
from utils.retry import retry_async

logger = get_logger(__name__)


@retry_async(exceptions=(PlaywrightTimeoutError, Exception))
async def scrape_insider_data(url: str) -> Dict[str, Any]:
    """
    Scrape insider trading data from insiderscreener.com
    
    Args:
        url: Company URL on insiderscreener.com
        
    Returns:
        Dictionary containing scraped data including transactions and company info
        
    Raises:
        Exception: If scraping fails after retries
    """
    logger.info(f"Starting scrape for {url}")
    
    async with async_playwright() as p:
        # Launch browser with configuration
        browser = await p.chromium.launch(
            headless=SCRAPER_CONFIG["headless"]
        )
        page = await browser.new_page()
        
        # Set timeout
        page.set_default_timeout(SCRAPER_CONFIG["timeout"])
        
        try:
            # Navigate to page
            logger.debug(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for table to load
            table_selector = '#search_bar_div > div.mx-lg-2.mb-3 > div > div > div:nth-child(9) > div.table-responsive-md > table > tbody'
            await page.wait_for_selector(
                table_selector,
                timeout=SCRAPER_CONFIG["wait_for_selector_timeout"]
            )
            
            # Extract company information
            company_name = await page.locator('h1').text_content()
            logger.info(f"Scraping data for: {company_name}")
            
            # Extract table data with proper column alignment
            transactions = await _extract_transactions(page)
            logger.debug(f"Extracted {len(transactions)} transactions")
            
            # Extract additional company metrics
            company_info = await _extract_company_info(page)
            
            await browser.close()
            
            result = {
                'scraped_at': datetime.now().isoformat(),
                'url': url,
                'company_info': company_info,
                'transactions': transactions,
                'total_transactions': len(transactions)
            }
            
            logger.info(f"Successfully scraped {company_name}: {len(transactions)} transactions")
            return result
            
        except Exception as e:
            logger.error(f"Error during scraping {url}: {str(e)}")
            await browser.close()
            raise


async def _extract_transactions(page) -> list:
    """
    Extract transaction data from table
    
    Args:
        page: Playwright page object
        
    Returns:
        List of transaction dictionaries
    """
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
                    // Handle both SEK, USD, and EUR values
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
    
    return transactions


async def _extract_company_info(page) -> Dict[str, str]:
    """
    Extract company metrics and information
    
    Args:
        page: Playwright page object
        
    Returns:
        Dictionary with company information
    """
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
    
    return company_info
