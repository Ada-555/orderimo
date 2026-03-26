"""Checkout forms."""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    address_line1 = forms.CharField(max_length=80)
    address_line2 = forms.CharField(max_length=80, required=False)
    city = forms.CharField(max_length=40)
    county = forms.CharField(max_length=80, required=False)
    postcode = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=2)  # ISO code e.g. "IE", "GB"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("full_name", css_class="form-group col-12 mb-3"),
            ),
            Row(
                Column("email", css_class="form-group col-md-6 mb-3"),
                Column("phone", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("address_line1", css_class="form-group col-12 mb-3"),
            ),
            Row(
                Column("address_line2", css_class="form-group col-12 mb-3"),
            ),
            Row(
                Column("city", css_class="form-group col-md-4 mb-3"),
                Column("county", css_class="form-group col-md-4 mb-3"),
                Column("postcode", css_class="form-group col-md-4 mb-3"),
            ),
            "country",
            Submit("submit", "Place Order", css_class="btn-primary btn-lg w-100"),
        )
