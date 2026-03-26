"""Global views — 404 handler and index redirect."""

from django.shortcuts import render


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)
