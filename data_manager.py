"""
Data Manager for Insider Trading Data
Handles data persistence, historical tracking, and change detection
"""

import json
from datetime import datetime
from pathlib import Path
import hashlib
from typing import Dict, Any, Optional
from config import DATA_CONFIG
from utils.logging_config import get_logger

logger = get_logger(__name__)


class InsiderDataManager:
    """Manages insider trading data with historical tracking and change detection"""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize data manager
        
        Args:
            base_dir: Base directory for data storage (default from config)
        """
        if base_dir is None:
            base_dir = DATA_CONFIG["base_dir"]
            
        self.base_dir = Path(base_dir)
        self.current_dir = self.base_dir / "current"
        self.history_dir = self.base_dir / "history"
        self.changes_dir = self.base_dir / "changes"
        
        # Create directories
        self.current_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.changes_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Data manager initialized with base_dir: {self.base_dir}")
    
    def _transaction_hash(self, transaction: Dict[str, Any]) -> str:
        """
        Create a unique hash for a transaction
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            MD5 hash of transaction key fields
        """
        key = (
            f"{transaction['notification_date']}_"
            f"{transaction['transaction_date']}_"
            f"{transaction['insider_name']}_"
            f"{transaction['number_of_shares']}_"
            f"{transaction['value']}"
        )
        return hashlib.md5(key.encode()).hexdigest()
    
    def detect_changes(
        self,
        old_data: Optional[Dict[str, Any]],
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect changes between old and new data
        
        Args:
            old_data: Previous scrape data (None if first scrape)
            new_data: New scrape data
            
        Returns:
            Dictionary with change information
        """
        if not old_data:
            return {
                'has_changes': True,
                'new_transactions': len(new_data['transactions']),
                'removed_transactions': 0,
                'modified_transactions': 0,
                'details': {
                    'type': 'initial_load',
                    'message': 'First time scraping this company'
                }
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
        
        has_changes = (
            len(new_transaction_hashes) > 0 or
            len(removed_transaction_hashes) > 0 or
            metrics_changed
        )
        
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
        
        logger.debug(
            f"Change detection complete: "
            f"new={len(new_transaction_hashes)}, "
            f"removed={len(removed_transaction_hashes)}, "
            f"metrics_changed={metrics_changed}"
        )
        
        return changes
    
    def save_data(
        self,
        company_slug: str,
        data: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> Path:
        """
        Save data with historical tracking
        
        Args:
            company_slug: Company identifier
            data: Scrape data to save
            changes: Change detection results
            
        Returns:
            Path to saved current file
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Save to current directory
        current_file = self.current_dir / f"{company_slug}.json"
        with open(current_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved current data for {company_slug}")
        
        # Save to history only if there are changes
        if changes['has_changes']:
            company_history_dir = self.history_dir / company_slug
            company_history_dir.mkdir(exist_ok=True)
            
            history_file = company_history_dir / f"{timestamp}.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Created historical snapshot for {company_slug}")
            
            # Save change log
            self._update_change_log(company_slug, data, changes, timestamp)
        
        return current_file
    
    def _update_change_log(
        self,
        company_slug: str,
        data: Dict[str, Any],
        changes: Dict[str, Any],
        timestamp: str
    ) -> None:
        """
        Update change log for a company
        
        Args:
            company_slug: Company identifier
            data: Scrape data
            changes: Change detection results
            timestamp: Timestamp string
        """
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
        
        # Keep only last N changes
        max_history = DATA_CONFIG["max_change_history"]
        change_log['changes'] = change_log['changes'][-max_history:]
        
        with open(change_log_file, 'w', encoding='utf-8') as f:
            json.dump(change_log, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Updated change log for {company_slug}")
    
    def load_current_data(self, company_slug: str) -> Optional[Dict[str, Any]]:
        """
        Load current data for a company
        
        Args:
            company_slug: Company identifier
            
        Returns:
            Current data dictionary or None if not found
        """
        current_file = self.current_dir / f"{company_slug}.json"
        if current_file.exists():
            with open(current_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded current data for {company_slug}")
            return data
        
        logger.debug(f"No current data found for {company_slug}")
        return None
    
    def get_change_history(self, company_slug: str) -> Optional[Dict[str, Any]]:
        """
        Get change history for a company
        
        Args:
            company_slug: Company identifier
            
        Returns:
            Change log dictionary or None if not found
        """
        change_log_file = self.changes_dir / f"{company_slug}_changes.json"
        if change_log_file.exists():
            with open(change_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
