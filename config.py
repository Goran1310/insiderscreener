"""
Configuration settings for Insider Screener
"""

# Company list for tracking
COMPANIES = [
    {
        "slug": "afry-ab",
        "name": "AFRY AB",
        "url": "https://www.insiderscreener.com/en/company/afry-ab"
    },
    {
        "slug": "academedia-ab",
        "name": "AcadeMedia AB",
        "url": "https://www.insiderscreener.com/en/company/academedia-ab"
    },
    {
        "slug": "akelius-residential-property-ab",
        "name": "Akelius Residential Property AB",
        "url": "https://www.insiderscreener.com/en/company/akelius-residential-property-ab"
    },
    {
        "slug": "byggmax-group-ab",
        "name": "Byggmax Group AB",
        "url": "https://www.insiderscreener.com/en/company/byggmax-group-ab"
    },
    {
        "slug": "bouvet-asa",
        "name": "Bouvet ASA",
        "url": "https://www.insiderscreener.com/en/company/bouvet-asa"
    },
    {
        "slug": "bravida-holding-ab",
        "name": "Bravida Holding AB",
        "url": "https://www.insiderscreener.com/en/company/bravida-holding-ab"
    },
    {
        "slug": "essity-ab-publ",
        "name": "Essity AB",
        "url": "https://www.insiderscreener.com/en/company/essity-ab-publ"
    },
    {
        "slug": "scandic-hotels-group-ab",
        "name": "Scandic Hotels Group AB",
        "url": "https://www.insiderscreener.com/en/company/scandic-hotels-group-ab"
    },
    {
        "slug": "rvrc-holding-ab",
        "name": "RVRC Holding AB",
        "url": "https://www.insiderscreener.com/en/company/rvrc-holding-ab"
    },
    {
        "slug": "eqt-ab",
        "name": "EQT AB",
        "url": "https://www.insiderscreener.com/en/company/eqt-ab"
    },
    {
        "slug": "inwido-ab-publ",
        "name": "Inwido AB",
        "url": "https://www.insiderscreener.com/en/company/inwido-ab-publ"
    },
    {
        "slug": "vbg-group-ab-publ",
        "name": "VBG Group AB",
        "url": "https://www.insiderscreener.com/en/company/vbg-group-ab-publ"
    },
]

# Scraper configuration
SCRAPER_CONFIG = {
    "headless": True,
    "timeout": 30000,
    "wait_for_selector_timeout": 10000,
    "retry_attempts": 3,
    "retry_delay_base": 2,  # Base delay for exponential backoff (seconds)
    "max_concurrent": 3,  # For future parallel scraping
}

# Data management configuration
DATA_CONFIG = {
    "base_dir": "data",
    "max_change_history": 100,  # Keep last N changes in log
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "scraper.log",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# Email notification configuration
EMAIL_CONFIG = {
    "enabled": True,  # Set to False to disable email notifications
    "send_summary": False,  # Send summary email after scraping all companies
}

# Load email credentials from environment variables (if available)
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SEND_NOTIFICATIONS = os.getenv("SEND_NOTIFICATIONS", "true").lower() == "true"
SEND_SUMMARY = os.getenv("SEND_SUMMARY", "false").lower() == "true"
