# pets/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ContactLinkFormSet, PetForm, PetOwnerProfileForm
from .models import PetOwner


def _require_pet_owner(request):
    """
    Shared guard for all pet owner views.
    Returns a redirect response if the user should not be here, or None if ok.
    Usage: guard = _require_pet_owner(request); if guard: return guard
    """
    if request.user.role != "pet_owner":
        return redirect("admin_dashboard")
    return None


# ---------------------------------------------------------------------------
# Onboarding — Step 1: Profile Info
# ---------------------------------------------------------------------------


@login_required
def onboarding_step1(request):
    # Role check — admin must never land here
    guard = _require_pet_owner(request)
    if guard:
        return guard

    # If already onboarded, skip the whole flow
    if request.user.is_onboarded:
        return redirect("owner_dashboard")

    if request.method == "POST":
        profile_form = PetOwnerProfileForm(request.POST, request.FILES)
        link_formset = ContactLinkFormSet(request.POST, prefix="links")

        if profile_form.is_valid() and link_formset.is_valid():
            # Save the PetOwner record linked to this user
            pet_owner = profile_form.save(commit=False)
            pet_owner.user = request.user
            pet_owner.save()

            # Save contact links — skip blank rows
            for form in link_formset:
                if form.is_valid() and not form.is_empty():
                    link = form.save(commit=False)
                    link.owner = pet_owner
                    link.save()

            # Store the new owner's PK in the session so Step 2 can find it
            # without a DB query on the user object.
            # This is cleared after Step 2 completes.
            request.session["onboarding_owner_id"] = pet_owner.pk

            return redirect("owner_onboarding_step2")

    else:
        profile_form = PetOwnerProfileForm()
        link_formset = ContactLinkFormSet(prefix="links")

    return render(
        request,
        "owner/onboarding/step1.html",
        {
            "profile_form": profile_form,
            "link_formset": link_formset,
            # Used by the template to show which step is active
            "current_step": 1,
        },
    )


# ---------------------------------------------------------------------------
# Onboarding — Step 2: Add First Pet
# ---------------------------------------------------------------------------


@login_required
def onboarding_step2(request):
    # Role check
    guard = _require_pet_owner(request)
    if guard:
        return guard

    # If already onboarded, skip the whole flow
    if request.user.is_onboarded:
        return redirect("owner_dashboard")

    # Guard: Step 2 requires Step 1 to have been completed first.
    # If someone navigates directly to step 2 without a session key,
    # send them back to step 1.
    owner_id = request.session.get("onboarding_owner_id")
    if not owner_id:
        return redirect("owner_onboarding_step1")

    # Safely fetch the PetOwner — if something is wrong, restart onboarding
    try:
        pet_owner = PetOwner.objects.get(pk=owner_id, user=request.user)
    except PetOwner.DoesNotExist:
        return redirect("owner_onboarding_step1")

    if request.method == "POST":
        # --- "Skip" button submitted ---
        # The skip button posts a hidden field: action=skip
        if request.POST.get("action") == "skip":
            _complete_onboarding(request)
            return redirect("owner_dashboard")

        # --- Pet form submitted ---
        pet_form = PetForm(request.POST, request.FILES)
        if pet_form.is_valid():
            pet = pet_form.save(commit=False)
            pet.owner = pet_owner
            pet.save()

            _complete_onboarding(request)
            messages.success(
                request,
                f"{pet.name} has been added. Welcome to Hapi Vet!",
            )
            return redirect("owner_dashboard")

    else:
        pet_form = PetForm()

    return render(
        request,
        "owner/onboarding/step2.html",
        {
            "pet_form": pet_form,
            "pet_owner": pet_owner,
            "current_step": 2,
        },
    )


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _complete_onboarding(request):
    """
    Marks the user as onboarded and cleans up the session key.
    Called from Step 2 on both save and skip.
    """
    request.user.is_onboarded = True
    request.user.save(update_fields=["is_onboarded"])
    # Clean up — no longer needed after onboarding completes
    request.session.pop("onboarding_owner_id", None)


# ---------------------------------------------------------------------------
# Profile — View
# ---------------------------------------------------------------------------


@login_required
def owner_profile(request):
    # Role check
    guard = _require_pet_owner(request)
    if guard:
        return guard

    # Fetch the owner record — if missing, something went wrong in onboarding
    try:
        pet_owner = PetOwner.objects.get(user=request.user)
    except PetOwner.DoesNotExist:
        # Safety net — reset onboarding flag and send them back through
        request.user.is_onboarded = False
        request.user.save(update_fields=["is_onboarded"])
        return redirect("owner_onboarding_step1")

    contact_links = pet_owner.contact_links.all()

    return render(
        request,
        "owner/profile/index.html",
        {
            "pet_owner": pet_owner,
            "contact_links": contact_links,
        },
    )


# ---------------------------------------------------------------------------
# Profile — Edit
# ---------------------------------------------------------------------------


@login_required
def owner_profile_edit(request):
    # Role check
    guard = _require_pet_owner(request)
    if guard:
        return guard

    try:
        pet_owner = PetOwner.objects.get(user=request.user)
    except PetOwner.DoesNotExist:
        request.user.is_onboarded = False
        request.user.save(update_fields=["is_onboarded"])
        return redirect("owner_onboarding_step1")

    if request.method == "POST":
        profile_form = PetOwnerProfileForm(
            request.POST,
            request.FILES,
            instance=pet_owner,
        )
        link_formset = ContactLinkFormSet(request.POST, prefix="links")

        if profile_form.is_valid() and link_formset.is_valid():
            profile_form.save()

            # Handle contact links:
            # Delete all existing links and replace with new ones.
            # Simpler and safer than trying to match and update individual rows.
            pet_owner.contact_links.all().delete()
            for form in link_formset:
                if form.is_valid() and not form.is_empty():
                    link = form.save(commit=False)
                    link.owner = pet_owner
                    link.save()

            messages.success(request, "Profile updated successfully.")
            return redirect("owner_profile")

    else:
        profile_form = PetOwnerProfileForm(instance=pet_owner)
        # Pre-populate formset with existing contact links
        existing_links = pet_owner.contact_links.all()
        initial_data = [
            {"platform": link.platform, "url_or_handle": link.url_or_handle}
            for link in existing_links
        ]
        link_formset = ContactLinkFormSet(prefix="links", initial=initial_data)

    return render(
        request,
        "owner/profile/edit.html",
        {
            "profile_form": profile_form,
            "link_formset": link_formset,
            "pet_owner": pet_owner,
        },
    )
