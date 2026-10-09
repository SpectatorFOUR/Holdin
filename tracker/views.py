from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import floatformat
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import OpeningBalanceForm, TransactionForm
from .models import Transaction, get_balances, get_profile

PAGE_SIZE = 20


def _first_page(user):
    paginator = Paginator(Transaction.objects.filter(user=user), PAGE_SIZE)
    return paginator.page(1)


@login_required
def home(request):
    if not get_profile(request.user).opening_done:
        return redirect('setup')

    return render(request, 'tracker/home.html', {
        'balances': get_balances(request.user),
        'page_obj': _first_page(request.user),
        'form': TransactionForm(user=request.user),
    })


@login_required
def history(request):
    paginator = Paginator(Transaction.objects.filter(user=request.user), PAGE_SIZE)
    try:
        page_obj = paginator.page(request.GET.get('page', 1))
    except (EmptyPage, PageNotAnInteger):
        return JsonResponse({'html': '', 'next_page': ''})

    html = render_to_string('tracker/_history_rows.html', {'page_obj': page_obj})
    next_page = page_obj.next_page_number() if page_obj.has_next() else ''
    return JsonResponse({'html': html, 'next_page': next_page})


@login_required
@require_POST
def add_transaction(request, kind):
    if kind not in (Transaction.CREDIT, Transaction.DEBIT):
        raise Http404

    form = TransactionForm(request.POST, user=request.user, kind=kind)
    if not form.is_valid():
        errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    new_tx = form.save(commit=False)
    new_tx.user = request.user
    new_tx.type = kind
    new_tx.save()

    balances = {key: floatformat(value, '2g') for key, value in get_balances(request.user).items()}
    page_obj = _first_page(request.user)
    return JsonResponse({
        'ok': True,
        'balances': balances,
        'html': render_to_string('tracker/_history_rows.html', {'page_obj': page_obj}),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else '',
    })


@login_required
def setup_balance(request):
    profile = get_profile(request.user)
    if profile.opening_done:
        return redirect('home')

    if request.method == 'POST':
        form = OpeningBalanceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                for account in (Transaction.CASH, Transaction.BANK, Transaction.WALLET):
                    amount = form.cleaned_data[account]
                    if amount > 0:
                        Transaction.objects.create(
                            user=request.user,
                            type=Transaction.CREDIT,
                            account=account,
                            title='Opening balance',
                            amount=amount,
                            description='Starting balance entered when setting up the account.',
                            party='Opening balance',
                        )
                profile.opening_done = True
                profile.save()
            return redirect('home')
    else:
        form = OpeningBalanceForm()

    return render(request, 'tracker/setup.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('setup')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


