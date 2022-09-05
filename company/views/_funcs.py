from ..models import Company
from django.shortcuts import redirect


def f_test_func(self):
    return self.request.user.is_authenticated
