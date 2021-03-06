from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render, reverse

from .forms import AccountSignupForm


def register(request):
    if request.method == "POST":
        form = AccountSignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            login(request, user)
            messages.success(
                request, "Registration successful!", extra_tags="is-success"
            )
            return redirect("panel")

        else:
            return render(
                request=request,
                template_name="users/register.html",
                context={"form": form},
            )

    form = AccountSignupForm
    return render(
        request=request, template_name="users/register.html", context={"form": form}
    )


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(
                    request,
                    f"You are now logged in as {username}",
                    extra_tags="is-primary",
                )
                return redirect(reverse("panel"))
            else:
                messages.error(
                    request, "Invalid username or password.", extra_tags="is-danger"
                )
        else:
            messages.error(
                request, "Invalid username or password.", extra_tags="is-danger"
            )
    form = AuthenticationForm()
    return render(
        request=request, template_name="users/login.html", context={"form": form}
    )


def logout_request(request):
    logout(request)
    messages.success(request, "Logged out successfully!", extra_tags="is-success")
    return redirect("panel")
