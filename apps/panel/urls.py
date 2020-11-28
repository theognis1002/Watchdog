from django.urls import path
from . import views

urlpatterns = [
    path("", views.PanelView.as_view(), name="panel"),
    path("delete/<int:pk>/", views.ProductDeleteView.as_view(), name="product-delete"),
    path("settings/<int:pk>/", views.SettingsView.as_view(), name="settings"),
]
