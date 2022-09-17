from ..models import JRE
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Case, When, F


def generate_ledger(account, period_from:date=None, period_to:date=None):
    if not period_from: period_from = timezone.now().date() - timedelta(days=30)
    if not period_to: period_to = timezone.now().date()
    beginning_balance = JRE.objects.filter(account=account, date__lt=period_from).annotate(
        amount2=Sum(
            Case( When(group='d', then=F('amount')),
                  When(group='c', then=F('amount')*-1), default=0),
        )
    ).aggregate(Sum('amount2'))

    result = JRE.objects.filter(account=account, date__gte=period_from, date__lte=period_to).annotate(
        pair_account=F('pair__account__name'),
        debit=Sum(Case(
            When(group='d', then=F('amount')), default=0,
        )),
        credit=Sum(Case(
            When(group='c', then=F('amount')), default=0,
        )),
        balance=Sum(0)
    )

    if beginning_balance['amount2__sum'] is None: beginning_balance = 0
    else: beginning_balance = beginning_balance['amount2__sum']

    if account.normal == 'd':
        return result.order_by('date', '-debit'), beginning_balance
    return result.order_by('date', '-credit'), beginning_balance
