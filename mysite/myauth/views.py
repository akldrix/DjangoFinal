from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _, ngettext
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .models import Profile


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)


class AboutMeView(UpdateView):
    form_class = AvatarUpdateForm
    template_name = "myauth/about-me.html"
    success_url = reverse_lazy("myauth:about-me")

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")
    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect("/admin/")
    return render(request, "myauth/login.html", {"error": "Invalid login credetials"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")  # type: ignore

    http_method_names = ["get", "post", "options"]

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class UserDetailView(DetailView):
    model = User
    template_name = "myauth/user-detail.html"
    context_object_name = "viewed_user"

    def get_queryset(self):
        return User.objects.select_related("profile")


class UsersListView(ListView):
    template_name = "myauth/users.html"
    queryset = User.objects.prefetch_related("profile")
    context_object_name = "users"


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = AvatarUpdateForm
    template_name = "myauth/edit-profile.html"

    def test_func(self) -> bool:
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True

        profile = self.get_object()

        return self.request.user == profile.user

    def get_object(self):

        user_pk = self.kwargs.get("pk")

        profile, created = Profile.objects.get_or_create(user_id=user_pk)

        return profile

    def get_success_url(self):
        return reverse_lazy("myauth:user-detail", kwargs={"pk": self.object.user.pk})


class HelloView(View):
    welcome_message = _("Welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1> {self.welcome_message} </h1>\n<h2> {products_line} </h2>"
        )
