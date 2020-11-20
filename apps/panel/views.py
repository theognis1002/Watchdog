from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView

from .forms import AddProductForm
from .models import Product
from .utils import Watchdog


class PanelView(FormView):
    template_name = "panel/panel.html"
    form_class = AddProductForm
    success_url = reverse_lazy("panel")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        return context

    def form_valid(self, form):
        url = form.cleaned_data["product_url"]
        watchdog = Watchdog()
        watchdog.add_product(url)

        messages.success(self.request, "Product added successfully!")
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("panel")
