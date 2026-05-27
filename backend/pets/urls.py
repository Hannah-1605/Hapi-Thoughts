# pets/urls.py

from django.urls import path

from . import views

urlpatterns = [
    # --- Onboarding ---
    path(
        "owner/onboarding/step1/",
        views.onboarding_step1,
        name="owner_onboarding_step1",
    ),
    path(
        "owner/onboarding/step2/",
        views.onboarding_step2,
        name="owner_onboarding_step2",
    ),

    # --- Profile ---
    path(
        "owner/profile/",
        views.owner_profile,
        name="owner_profile",
    ),
    path(
        "owner/profile/edit/",
        views.owner_profile_edit,
        name="owner_profile_edit",
    ),
]