"""
Test email notifications for Insider Screener
"""

import sys
from datetime import datetime
from notifications import EmailNotifier
from config import EMAIL_USER, EMAIL_PASS, RECIPIENT_EMAIL

def test_email_notification():
    """Test sending email notification"""
    
    print("🧪 Testing Insider Screener Email Notifications\n")
    
    # Check credentials
    if not EMAIL_USER or not EMAIL_PASS or not RECIPIENT_EMAIL:
        print("❌ Email credentials not configured in .env file")
        print("Please create .env file with:")
        print("  EMAIL_USER=your-email@gmail.com")
        print("  EMAIL_PASS=your-app-password")
        print("  RECIPIENT_EMAIL=recipient@email.com")
        return False
    
    print(f"📧 Email User: {EMAIL_USER}")
    print(f"📧 Recipient: {RECIPIENT_EMAIL}")
    print()
    
    # Create notifier
    notifier = EmailNotifier(EMAIL_USER, EMAIL_PASS, RECIPIENT_EMAIL)
    
    # Test data - simulating new transactions
    test_transactions = [
        {
            'notification_date': '2025-12-25',
            'transaction_date': '2025-12-24',
            'transaction_type': 'Purchase',
            'insider_name': 'John Doe',
            'insider_position': 'CEO',
            'insider_role': 'Officer',
            'additional_info': 'Through affiliated company',
            'number_of_shares': '50,000',
            'price': '125.50',
            'price_calculated': '125.50',
            'value': 'SEK 6,275,000'
        },
        {
            'notification_date': '2025-12-25',
            'transaction_date': '2025-12-23',
            'transaction_type': 'Sale',
            'insider_name': 'Jane Smith',
            'insider_position': 'CFO',
            'insider_role': 'Officer',
            'additional_info': '',
            'number_of_shares': '25,000',
            'price': '120.00',
            'price_calculated': '120.00',
            'value': 'SEK 3,000,000'
        }
    ]
    
    print("📤 Sending test email with 2 sample transactions...")
    success = notifier.send_new_transactions_alert(
        company_name="Test Company AB (TEST)",
        company_slug="test-company",
        new_transactions=test_transactions
    )
    
    if success:
        print("\n✅ Test email sent successfully!")
        print(f"📬 Check your inbox at {RECIPIENT_EMAIL}")
        return True
    else:
        print("\n❌ Failed to send test email")
        print("Check the error messages above")
        return False


if __name__ == "__main__":
    success = test_email_notification()
    sys.exit(0 if success else 1)
