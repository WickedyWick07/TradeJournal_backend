from django.db import models
from users.models import CustomUser
from decimal import Decimal

# Brokers choices
BROKERS = [
    ('IG GROUP', 'IG Group'),
    ('OANDA', 'OANDA'),
    ('XM', 'XM'),
    ('ETORO', 'eToro'),
    ('SAXO BANK', 'Saxo Bank'),
    ('PEPPERSTONE', 'Pepperstone'),
    ('INTERACTIVE BROKERS', 'Interactive Brokers'),
    ('AVATRADE', 'AvaTrade'),
    ('FP MARKETS', 'FP Markets')
]

class TradingAccount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='trading_accounts', db_index=True)
    account_number = models.CharField(max_length=9, unique=True)  # Make account number unique
    account_balance = models.DecimalField(max_digits=10, decimal_places=2)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Static initial balance
    broker = models.CharField(max_length=50, choices=BROKERS)
    journal = models.OneToOneField('journal.AccountJournal', on_delete=models.CASCADE, related_name='trading_account', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user}'s trading account"
    
    
    def update_account_balance(self):
        if self.journal:  # Check if the journal exists
            journal_entries = self.journal.entries.all()

            total_pnl = Decimal(0)  # Initialize total P&L as a decimal
            for entry in journal_entries:
                total_pnl += entry.pnl if entry.pnl is not None else Decimal(0)

            # Ensure that initial_balance is not None, default to Decimal(0) if it is
            if self.initial_balance is None:
                print("Warning: initial_balance is None, defaulting to 0.")
                self.initial_balance = Decimal(0)

            # Perform the addition with the corrected initial_balance
            self.account_balance = self.initial_balance + total_pnl
            self.save()
        else:
            print("No journal attached to this account.")

    def save(self, *args, **kwargs):
        # Set the initial_balance to the account_balance on account creation
        if not self.pk:  # This ensures it only happens when the account is first created
            self.initial_balance = self.account_balance
        super().save(*args, **kwargs)
