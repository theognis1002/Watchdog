import logging

from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, UpdateView

from .forms import AddProductForm, WatchdogSettingsForm
from .models import Product, WatchdogSettings
from .utils import Watchdog

logging.basicConfig(format="    [-]%(process)d-%(levelname)s-%(message)s")


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
        try:
            watchdog = Watchdog()
            watchdog.add_product(url)

            messages.success(self.request, "Product added successfully!")
        except Exception as e:
            logging.error(f"{e.__class__.__name__} - {str(e)}")

        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("panel")


class SettingsView(UpdateView):
    template_name = "panel/settings.html"
    model = WatchdogSettings
    form_class = WatchdogSettingsForm
    success_url = reverse_lazy("settings", kwargs={"pk": 1})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        messages.success(self.request, "Successfully updated credential settings!")
        return super().form_valid(form)