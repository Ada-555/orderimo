"""Views for accounts app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from allauth.account.views import LoginView, LogoutView
from .models import Address
from .forms import SignupForm, AddressForm


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class CustomLogoutView(LogoutView):
    template_name = "accounts/logout.html"


def signup(request):
    if request.user.is_authenticated:
        return redirect("products:product_list")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created! Welcome aboard.")
            return redirect("products:product_list")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, "accounts/address_list.html", {"addresses": addresses})


@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            # Unset default if this is the new default
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(
                    is_default=False
                )
            address.save()
            messages.success(request, "Address saved.")
            return redirect("accounts:address_list")
    else:
        form = AddressForm()

    return render(request, "accounts/address_form.html", {"form": form, "action": "Create"})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            if form.cleaned_data["is_default"]:
                Address.objects.filter(user=request.user, is_default=True).exclude(
                    pk=pk
                ).update(is_default=False)
            form.save()
            messages.success(request, "Address updated.")
            return redirect("accounts:address_list")
    else:
        form = AddressForm(instance=address)

    return render(
        request, "accounts/address_form.html", {"form": form, "action": "Edit"}
    )


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted.")
        return redirect("accounts:address_list")
    return render(request, "accounts/address_confirm_delete.html", {"address": address})
