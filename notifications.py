"""
Email notification service for Insider Screener
Sends alerts when new insider trading transactions are detected
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime
from utils.logging_config import get_logger

logger = get_logger(__name__)


class EmailNotifier:
    """Handles email notifications for new insider trading transactions"""
    
    def __init__(self, email_user: str, email_pass: str, recipient_email: str):
        """
        Initialize email notifier
        
        Args:
            email_user: Gmail address to send from
            email_pass: Gmail app password
            recipient_email: Recipient email address
        """
        self.email_user = email_user
        self.email_pass = email_pass
        self.recipient_email = recipient_email
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_new_transactions_alert(
        self,
        company_name: str,
        company_slug: str,
        new_transactions: List[Dict[str, Any]]
    ) -> bool:
        """
        Send email alert for new transactions
        
        Args:
            company_name: Company display name
            company_slug: Company identifier
            new_transactions: List of new transaction dictionaries
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not new_transactions:
            logger.debug(f"No new transactions to notify for {company_slug}")
            return True
        
        try:
            subject = f"🚨 New Insider Trading: {company_name} ({len(new_transactions)} transaction{'s' if len(new_transactions) > 1 else ''})"
            html_content = self._format_transactions_html(company_name, company_slug, new_transactions)
            
            return self._send_email(subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def _format_transactions_html(
        self,
        company_name: str,
        company_slug: str,
        transactions: List[Dict[str, Any]]
    ) -> str:
        """
        Format transactions as HTML email
        
        Args:
            company_name: Company display name
            company_slug: Company identifier
            transactions: List of transaction dictionaries
            
        Returns:
            HTML formatted email content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #d32f2f; color: white; padding: 20px; border-radius: 5px; }}
                .company {{ font-size: 24px; font-weight: bold; }}
                .transaction {{ background-color: #f5f5f5; margin: 15px 0; padding: 15px; border-left: 4px solid #d32f2f; border-radius: 3px; }}
                .transaction-type {{ display: inline-block; padding: 4px 8px; border-radius: 3px; font-weight: bold; font-size: 12px; }}
                .purchase {{ background-color: #4caf50; color: white; }}
                .sale {{ background-color: #f44336; color: white; }}
                .field {{ margin: 5px 0; }}
                .label {{ font-weight: bold; color: #555; display: inline-block; width: 150px; }}
                .value {{ color: #000; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #777; }}
                .alert-icon {{ font-size: 32px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="alert-icon">🚨</div>
                <div class="company">{company_name}</div>
                <div>New Insider Trading Detected</div>
                <div style="font-size: 12px; margin-top: 10px;">Detected: {timestamp}</div>
            </div>
            
            <h2>New Transactions ({len(transactions)})</h2>
        """
        
        for idx, txn in enumerate(transactions, 1):
            transaction_type = txn.get('transaction_type', 'Unknown')
            is_purchase = 'purchase' in transaction_type.lower() or 'köp' in transaction_type.lower()
            type_class = 'purchase' if is_purchase else 'sale'
            type_emoji = '📈' if is_purchase else '📉'
            
            html += f"""
            <div class="transaction">
                <h3 style="margin-top: 0;">Transaction #{idx} {type_emoji}</h3>
                <span class="transaction-type {type_class}">{transaction_type}</span>
                
                <div class="field">
                    <span class="label">Notification Date:</span>
                    <span class="value">{txn.get('notification_date', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Transaction Date:</span>
                    <span class="value">{txn.get('transaction_date', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Insider:</span>
                    <span class="value">{txn.get('insider_name', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Position:</span>
                    <span class="value">{txn.get('insider_position', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Role:</span>
                    <span class="value">{txn.get('insider_role', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Number of Shares:</span>
                    <span class="value"><strong>{txn.get('number_of_shares', 'N/A')}</strong></span>
                </div>
                <div class="field">
                    <span class="label">Price (displayed):</span>
                    <span class="value">{txn.get('price', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Price (calculated):</span>
                    <span class="value">{txn.get('price_calculated', 'N/A')}</span>
                </div>
                <div class="field">
                    <span class="label">Total Value:</span>
                    <span class="value"><strong>{txn.get('value', 'N/A')}</strong></span>
                </div>
            """
            
            if txn.get('additional_info'):
                html += f"""
                <div class="field">
                    <span class="label">Additional Info:</span>
                    <span class="value">{txn.get('additional_info')}</span>
                </div>
                """
            
            html += "</div>"
        
        html += f"""
            <div class="footer">
                <p>📊 <strong>Company:</strong> {company_name} ({company_slug})</p>
                <p>🔗 <strong>Source:</strong> <a href="https://www.insiderscreener.com/en/company/{company_slug}">View on InsiderScreener</a></p>
                <p><em>Automated alert from Insider Screener Monitor</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, html_content: str) -> bool:
        """
        Send HTML email via Gmail SMTP
        
        Args:
            subject: Email subject
            html_content: HTML body content
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.email_user
            message['To'] = self.recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send via Gmail SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(message)
            
            logger.info(f"📧 Email notification sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_summary_notification(self, results: List[Dict[str, Any]]) -> bool:
        """
        Send summary of all companies with changes
        
        Args:
            results: List of result dictionaries from scraping run
            
        Returns:
            True if sent successfully, False otherwise
        """
        companies_with_changes = [r for r in results if r.get('has_changes') and r.get('new_transactions', 0) > 0]
        
        if not companies_with_changes:
            logger.debug("No changes detected, skipping summary email")
            return True
        
        try:
            total_new = sum(r.get('new_transactions', 0) for r in companies_with_changes)
            subject = f"📊 Insider Trading Summary: {len(companies_with_changes)} companies, {total_new} new transactions"
            
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #1976d2; color: white; padding: 20px; border-radius: 5px; }}
                    .company {{ background-color: #f5f5f5; margin: 10px 0; padding: 15px; border-left: 4px solid #1976d2; border-radius: 3px; }}
                    .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1 style="margin: 0;">📊 Insider Trading Summary</h1>
                    <p style="margin: 5px 0 0 0;">Detected: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <h2>Companies with New Transactions ({len(companies_with_changes)})</h2>
            """
            
            for result in companies_with_changes:
                html += f"""
                <div class="company">
                    <h3 style="margin-top: 0;">{result['name']}</h3>
                    <p><strong>New transactions:</strong> {result['new_transactions']}</p>
                    <p><a href="https://www.insiderscreener.com/en/company/{result['slug']}">View on InsiderScreener →</a></p>
                </div>
                """
            
            html += f"""
                <div class="footer">
                    <p><strong>Total new transactions:</strong> {total_new}</p>
                    <p><em>Automated summary from Insider Screener Monitor</em></p>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(subject, html)
            
        except Exception as e:
            logger.error(f"Failed to send summary email: {str(e)}")
            return False
