from django.db.models.signals import post_save 
from django.dispatch import receiver
from .models import JournalEntry 
from accounts.models import TradingAccount

@receiver(post_save, sender=JournalEntry)
def update_account_balance(sender, instance, created, **kwargs):
    trading_account= instance.journal.account 

    trading_account.update_account_balance()