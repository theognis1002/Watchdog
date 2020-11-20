from django import forms


class AddProductForm(forms.Form):
    product_url = forms.URLField(
        label="", widget=forms.TextInput(attrs={"placeholder": "Product URL"})
    )
