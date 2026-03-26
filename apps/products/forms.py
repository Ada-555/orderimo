"""Forms for products app."""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "sku",
            "name",
            "description",
            "price",
            "sale_price",
            "has_sizes",
            "stock",
            "is_available",
            "status",
            "image",
            "image_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-6 mb-3"),
                Column("sku", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("category", css_class="form-group col-md-6 mb-3"),
                Column("status", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("price", css_class="form-group col-md-4 mb-3"),
                Column("sale_price", css_class="form-group col-md-4 mb-3"),
                Column("stock", css_class="form-group col-md-4 mb-3"),
            ),
            "description",
            "has_sizes",
            "is_available",
            "image",
            "image_url",
            Submit("submit", "Save Product"),
        )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "friendly_name", "description", "image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-6 mb-3"),
                Column("friendly_name", css_class="form-group col-md-6 mb-3"),
            ),
            "description",
            "image",
            Submit("submit", "Save Category"),
        )
