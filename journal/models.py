from django.db import models
from users.models import CustomUser
from decimal import Decimal
from django.core.exceptions import ValidationError

RESULT_CHOICES = [('win', 'WIN'), ('loss', 'LOSS'), ('break-even', 'BREAK-EVEN')]
DIRECTION_CHOICES = [('long', 'LONG'), ('short', 'SHORT')]

class AccountJournal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account = models.OneToOneField('accounts.TradingAccount', on_delete=models.CASCADE, related_name='journal_entry')
    title = models.CharField(default='Trading Journal', max_length=100)

    def __str__(self):
        return f"{self.title} for {self.account.user}'s trading account"




class JournalEntry(models.Model):
    journal = models.ForeignKey('journal.AccountJournal', on_delete=models.CASCADE, related_name='entries')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    entry_price = models.DecimalField(max_digits=10, decimal_places=5)
    stop_loss_price = models.DecimalField(max_digits=10, decimal_places=5)
    lot_size = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    target_price = models.DecimalField(max_digits=10, decimal_places=5)
    result = models.CharField(max_length=50, choices=RESULT_CHOICES)
    direction = models.CharField(max_length=5, choices=DIRECTION_CHOICES, null=True)  # New field
    pair = models.CharField(max_length=50)
    textarea = models.TextField(max_length=500, blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    created_at = models.DateTimeField(auto_now_add=True)
    pnl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user}'s {self.direction} trade entry for {self.pair}"
    
    def calculate_pnl(self):
        if not self.lot_size:
            return Decimal('0.00')
        
        standard_lot_value = Decimal('100000')  # Value of 1 standard lot
        pip_value_per_lot = Decimal('10.00')  # Pip value for 1 standard lot
        
        if self.result == 'win':
            price_difference = self.target_price - self.entry_price if self.direction == 'long' else self.entry_price - self.target_price
        elif self.result == 'loss':
            price_difference = self.stop_loss_price - self.entry_price if self.direction == 'long' else self.entry_price - self.stop_loss_price
        else:
            return Decimal('0.00')
        
        pips = price_difference * Decimal('10000')  # Convert to pips
        lot_fraction = self.lot_size / Decimal('1.00')  # Convert lot size to a fraction of a standard lot
        pnl = pips * lot_fraction * pip_value_per_lot
        
        return pnl.quantize(Decimal('0.01'))  # Round to 2 decimal places

    def clean(self):
        super().clean()
        if self.direction == 'long':
            if self.result == 'win' and self.target_price <= self.entry_price:
                raise ValidationError("For a winning long trade, the target price must be higher than the entry price.")
            if self.result == 'loss' and self.stop_loss_price >= self.entry_price:
                raise ValidationError("For a losing long trade, the stop loss price must be lower than the entry price.")
        elif self.direction == 'short':
            if self.result == 'win' and self.target_price >= self.entry_price:
                raise ValidationError("For a winning short trade, the target price must be lower than the entry price.")
            if self.result == 'loss' and self.stop_loss_price <= self.entry_price:
                raise ValidationError("For a losing short trade, the stop loss price must be higher than the entry price.")
        
        calculated_pnl = self.calculate_pnl()
        if calculated_pnl < 0 and self.result == 'win':
            raise ValidationError("PNL cannot be negative for a winning trade.")
        if calculated_pnl > 0 and self.result == 'loss':
            raise ValidationError("PNL cannot be positive for a losing trade.")

    def save(self, *args, **kwargs):
        self.full_clean()  # This will call the clean method
        self.pnl = self.calculate_pnl()
        super(JournalEntry, self).save(*args, **kwargs)


class JournalImage(models.Model):
    entry = models.ForeignKey(JournalEntry, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='journal_images/')
    created_at = models.DateTimeField(auto_now_add=True)
