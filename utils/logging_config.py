"""
Logging configuration for Insider Screener
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import LOGGING_CONFIG


def setup_logging(name: str = "insiderscreener") -> logging.Logger:
    """
    Set up logging with both file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = Path(LOGGING_CONFIG["log_file"])
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOGGING_CONFIG["max_bytes"],
        backupCount=LOGGING_CONFIG["backup_count"],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "insiderscreener") -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logging(name)
    
    return logger
