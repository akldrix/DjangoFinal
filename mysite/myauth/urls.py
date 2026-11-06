from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    AboutMeView,
    FooBarView,
    MyLogoutView,
    RegisterView,
    UserDetailView,
    UserProfileUpdateView,
    get_cookie_view,
    get_session_view,
    set_cookie_view,
    set_session_view,
    UsersListView,
    HelloView,
)

app_name = "myauth"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        MyLogoutView.as_view(),
        name="logout",
    ),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/edit/", UserProfileUpdateView.as_view(), name="user-edit"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("register/", RegisterView.as_view(), name="register"),
    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
    path("hello/", HelloView.as_view(), name="hello"),
]
