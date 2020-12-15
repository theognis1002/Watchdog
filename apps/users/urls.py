from django.urls import path
from . import views

urlpatterns = [
    path(
        "5659609d-f7c7-40ed-8ecf-200e7520d6bf/register/",
        views.register,
        name="register",
    ),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
]
