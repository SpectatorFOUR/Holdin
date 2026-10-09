from decimal import Decimal

from django import forms

from .models import Transaction, get_balances


class OpeningBalanceForm(forms.Form):
    cash = forms.DecimalField(label='In Cash', min_value=Decimal('0'), max_digits=12, decimal_places=2, initial=0)
    bank = forms.DecimalField(label='In Bank Account', min_value=Decimal('0'), max_digits=12, decimal_places=2, initial=0)
    wallet = forms.DecimalField(label='In Mobile Wallet', min_value=Decimal('0'), max_digits=12, decimal_places=2, initial=0)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'account', 'party', 'description', 'date_time']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'inputmode': 'decimal'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, user=None, kind=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.kind = kind
        self.fields['description'].required = False
        self.fields['account'].choices = [('', 'Select account')] + list(Transaction.ACCOUNT_CHOICES)
        self.fields['date_time'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']

    def clean(self):
        cleaned = super().clean()
        if self.kind == Transaction.DEBIT and self.user is not None:
            amount = cleaned.get('amount')
            account = cleaned.get('account')
            if amount is not None and account:
                available = get_balances(self.user)[account]
                if amount > available:
                    name = dict(Transaction.ACCOUNT_CHOICES)[account]
                    self.add_error('amount', f'Not enough money in {name}. Available: Rs. {available:,.2f}')
        return cleaned


    