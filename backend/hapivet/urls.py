from django.urls import path, include

urlpatterns = [
    # accounts (login, register, etc.)
    path("", include("accounts.urls")),
    # allauth (Google OAuth, email verification, etc.)
    path("accounts/", include("allauth.urls")),
]