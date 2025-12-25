"""
Insider Screener - Main Entry Point
Track insider trading data from insiderscreener.com with historical tracking
"""

import asyncio
import argparse
import sys
from typing import List, Dict, Any
from config import COMPANIES, SCRAPER_CONFIG, EMAIL_USER, EMAIL_PASS, RECIPIENT_EMAIL, SEND_NOTIFICATIONS, SEND_SUMMARY
from data_manager import InsiderDataManager
from scraper import scrape_insider_data
from notifications import EmailNotifier
from utils.logging_config import setup_logging, get_logger

# Setup logging
logger = setup_logging()


async def process_company(
    company: Dict[str, str],
    manager: InsiderDataManager,
    notifier: EmailNotifier,
    total_companies: int,
    index: int
) -> Dict[str, Any]:
    """
    Process a single company: scrape, detect changes, save data, send notifications
    
    Args:
        company: Company dictionary with slug, name, url
        manager: Data manager instance
        notifier: Email notifier instance
        total_companies: Total number of companies being processed
        index: Current company index (1-based)
        
    Returns:
        Dictionary with processing results
    """
    company_slug = company["slug"]
    company_name = company["name"]
    url = company["url"]
    
    logger.info(f"[{index}/{total_companies}] Processing: {company_name} ({company_slug})")
    logger.info("-" * 60)
    
    result = {
        'slug': company_slug,
        'name': company_name,
        'success': False,
        'has_changes': False,
        'new_transactions': 0,
        'error': None
    }
    
    try:
        # Load previous data
        old_data = manager.load_current_data(company_slug)
        if old_data:
            logger.info(f"Loaded previous data from {old_data['scraped_at']}")
        else:
            logger.info("No previous data found - first scrape")
        
        # Scrape new data
        new_data = await scrape_insider_data(url)
        
        # Detect changes
        changes = manager.detect_changes(old_data, new_data)
        
        if changes['has_changes']:
            logger.info("📊 CHANGES DETECTED")
            
            if changes['new_transactions'] > 0:
                logger.info(f"   ✨ New transactions: {changes['new_transactions']}")
                result['new_transactions'] = changes['new_transactions']
                
                # Log sample transactions
                if 'new_transactions_list' in changes['details']:
                    for txn in changes['details']['new_transactions_list'][:2]:
                        logger.info(
                            f"      • {txn['transaction_date']} - "
                            f"{txn['insider_name']}: {txn['transaction_type']}"
                        )
            
            if changes['removed_transactions'] > 0:
                logger.info(f"   🗑️  Removed transactions: {changes['removed_transactions']}")
            
            if changes.get('metrics_changed'):
                logger.info("   📈 Company metrics changed")
            
            result['has_changes'] = True
            
            # Save data with history
            saved_file = manager.save_data(company_slug, new_data, changes)
            logger.info("   ✓ Data saved with historical snapshot")
            
            # Send email notification for new transactions
            if notifier and changes['new_transactions'] > 0:
                new_txn_list = changes['details'].get('new_transactions_list', [])
                if new_txn_list:
                    logger.info(f"   📧 Sending email notification for {len(new_txn_list)} new transactions")
                    notifier.send_new_transactions_alert(
                        company_name=company_name,
                        company_slug=company_slug,
                        new_transactions=new_txn_list
                    )
            
        else:
            logger.info("No changes detected - data is up to date")
            # Still update current file with new timestamp
            saved_file = manager.save_data(company_slug, new_data, changes)
            logger.info("Current data refreshed")
        
        logger.info(f"Company: {new_data['company_info']['company_name'].strip()}")
        logger.info(f"Total Transactions: {new_data['total_transactions']}")
        
        result['success'] = True
        
    except Exception as e:
        error_msg = f"Error scraping {company_slug}: {str(e)}"
        logger.error(error_msg)
        result['error'] = str(e)
    
    return result


async def scrape_companies(companies: List[Dict[str, str]]) -> None:
    """
    Scrape multiple companies and generate summary
    
    Args:
        companies: List of company dictionaries
    """
    # Initialize data manager
    manager = InsiderDataManager()
    
    # Initialize email notifier (if configured)
    notifier = None
    if SEND_NOTIFICATIONS and EMAIL_USER and EMAIL_PASS and RECIPIENT_EMAIL:
        notifier = EmailNotifier(EMAIL_USER, EMAIL_PASS, RECIPIENT_EMAIL)
        logger.info("📧 Email notifications enabled")
    else:
        logger.info("📧 Email notifications disabled")
    
    logger.info("=" * 60)
    logger.info(f"INSIDER SCREENER - TRACKING {len(companies)} COMPANIES")
    logger.info("=" * 60)
    
    results = []
    
    for idx, company in enumerate(companies, 1):
        result = await process_company(company, manager, notifier, len(companies), idx)
        results.append(result)
        logger.info("")  # Empty line between companies
    
    # Generate summary
    print_summary(results)
    
    # Send summary email if enabled
    if notifier and SEND_SUMMARY:
        logger.info("📧 Sending summary email...")
        notifier.send_summary_notification(results)


def print_summary(results: List[Dict[str, Any]]) -> None:
    """
    Print summary of scraping results
    
    Args:
        results: List of processing results
    """
    total_companies = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total_companies - successful
    companies_with_changes = [r for r in results if r['has_changes']]
    total_new_transactions = sum(r['new_transactions'] for r in results)
    
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Companies tracked: {total_companies}")
    logger.info(f"Successful: {successful}")
    if failed > 0:
        logger.info(f"Failed: {failed}")
    logger.info(f"Companies with changes: {len(companies_with_changes)}")
    logger.info(f"Total new transactions: {total_new_transactions}")
    
    if companies_with_changes:
        logger.info("\nCompanies updated:")
        for result in companies_with_changes:
            logger.info(f"  • {result['name']} ({result['slug']}): {result['new_transactions']} new")
    
    if failed > 0:
        logger.info("\nFailed companies:")
        for result in results:
            if not result['success']:
                logger.info(f"  • {result['name']} ({result['slug']}): {result['error']}")
    
    logger.info("=" * 60)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Scrape insider trading data from insiderscreener.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all companies
  python main.py --all
  
  # Scrape specific companies by slug
  python main.py --companies afry-ab bouvet-asa
  
  # Run in headful mode (show browser)
  python main.py --all --no-headless
  
  # List all tracked companies
  python main.py --list
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all',
        action='store_true',
        help='Scrape all tracked companies'
    )
    group.add_argument(
        '--companies',
        nargs='+',
        metavar='SLUG',
        help='Scrape specific companies by slug (e.g., afry-ab bouvet-asa)'
    )
    group.add_argument(
        '--list',
        action='store_true',
        help='List all tracked companies'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in headful mode (visible)'
    )
    
    return parser.parse_args()


def list_companies() -> None:
    """List all tracked companies"""
    print(f"\nTracked Companies ({len(COMPANIES)}):")
    print("=" * 60)
    for company in COMPANIES:
        print(f"  {company['slug']:<40} {company['name']}")
    print("=" * 60)


async def main() -> None:
    """Main entry point"""
    args = parse_arguments()
    
    # List companies and exit
    if args.list:
        list_companies()
        return
    
    # Override headless setting if requested
    if args.no_headless:
        SCRAPER_CONFIG['headless'] = False
        logger.info("Running in headful mode (browser visible)")
    
    # Determine which companies to scrape
    if args.all:
        companies_to_scrape = COMPANIES
        logger.info(f"Scraping all {len(COMPANIES)} companies")
    else:
        # Filter companies by slug
        company_slugs = set(args.companies)
        companies_to_scrape = [c for c in COMPANIES if c['slug'] in company_slugs]
        
        # Check for invalid slugs
        found_slugs = {c['slug'] for c in companies_to_scrape}
        invalid_slugs = company_slugs - found_slugs
        if invalid_slugs:
            logger.error(f"Unknown company slugs: {', '.join(invalid_slugs)}")
            logger.info("Use --list to see all tracked companies")
            sys.exit(1)
        
        logger.info(f"Scraping {len(companies_to_scrape)} selected companies")
    
    # Run scraper
    await scrape_companies(companies_to_scrape)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
