from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Transaction(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    CASH = 'cash'
    BANK = 'bank'
    WALLET = 'wallet'
    ACCOUNT_CHOICES = [
        (CASH, 'Cash'),
        (BANK, 'Bank Account'),
        (WALLET, 'Mobile Wallet'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    account = models.CharField(max_length=6, choices=ACCOUNT_CHOICES)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField(blank=True)
    party = models.CharField(max_length=100)
    date_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_time', '-id']

    def __str__(self):
        return f'{self.get_type_display()} Rs. {self.amount} - {self.title}'


def get_balances(user):
    """Return the balance of each account and the total for one user."""
    transactions = Transaction.objects.filter(user=user)
    balances = {}
    for key, _label in Transaction.ACCOUNT_CHOICES:
        credits = transactions.filter(account=key, type=Transaction.CREDIT).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        debits = transactions.filter(account=key, type=Transaction.DEBIT).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        balances[key] = credits - debits
    balances['total'] = balances['cash'] + balances['bank'] + balances['wallet']
    return balances


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    opening_done = models.BooleanField(default=False)

    def __str__(self):
        return f'Profile of {self.user}'


def get_profile(user):
    """Return the profile of a user, creating it the first time."""
    profile, _created = Profile.objects.get_or_create(user=user)
    return profile

