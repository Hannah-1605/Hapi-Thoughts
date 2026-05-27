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


    # --- Pets ---
    path(
        "owner/pets/",
        views.owner_pet_list,
        name="owner_pet_list",
    ),
    path(
        "owner/pets/add/",
        views.owner_pet_add,
        name="owner_pet_add",
    ),
    path(
        "owner/pets/<int:pk>/",
        views.owner_pet_detail,
        name="owner_pet_detail",
    ),
    path(
        "owner/pets/<int:pk>/edit/",
        views.owner_pet_edit,
        name="owner_pet_edit",
    ),
    path(
        "owner/pets/<int:pk>/delete-request/",
        views.owner_pet_delete_request,
        name="owner_pet_delete_request",
    ),
    path(
        "owner/pets/<int:pk>/cancel-delete-request/",
        views.owner_pet_cancel_delete_request,
        name="owner_pet_cancel_delete_request",
    ),

]