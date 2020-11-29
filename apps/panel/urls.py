from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path("", login_required(views.PanelView.as_view()), name="panel"),
    path(
        "delete/<int:pk>/",
        login_required(views.ProductDeleteView.as_view()),
        name="product-delete",
    ),
    path(
        "settings/<int:pk>/",
        login_required(views.SettingsView.as_view()),
        name="settings",
    ),
]
