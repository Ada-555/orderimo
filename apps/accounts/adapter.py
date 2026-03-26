"""Custom allauth adapter to handle multiple auth backends."""

from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import login


class AccountAdapter(DefaultAccountAdapter):

    def login(self, request, user):
        """Login with explicit backend to avoid ambiguity with multiple backends."""
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
