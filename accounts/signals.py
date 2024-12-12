# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TradingAccount
from journal.models import AccountJournal

@receiver(post_save, sender=TradingAccount)
def create_journal_for_account(sender, instance, created, **kwargs):
    if created:
        # Create a Journal for the newly created TradingAccount
        journal = AccountJournal.objects.create(
            user=instance.user,
            title=f"{instance.user}'s Journal",
            account=instance  # Associate the journal with the TradingAccount
        )

        instance.journal = journal
        instance.save()
