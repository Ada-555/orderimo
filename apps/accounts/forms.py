"""Forms for accounts app."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Address

User = get_user_model()


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "username",
            "email",
            "password1",
            "password2",
            Submit("Sign Up", "Create Account", css_class="btn-primary w-100"),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            "name",
            "line1",
            "line2",
            "city",
            "county",
            "postcode",
            "country",
            "is_default",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("name"),
            Field("line1"),
            Field("line2"),
            Field("city"),
            Field("county"),
            Field("postcode"),
            Field("country"),
            Field("is_default"),
            Submit("Save Address", "Save Address"),
        )
