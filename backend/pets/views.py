# pets/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ContactLinkFormSet, PetForm, PetOwnerProfileForm
from .models import PetOwner

from .forms import ContactLinkFormSet, PetDeletionRequestForm, PetForm, PetOwnerProfileForm
from .models import Pet, PetDeletionRequest, PetOwner

from django.shortcuts import get_object_or_404, redirect, render


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


# ---------------------------------------------------------------------------
# Pets — List
# ---------------------------------------------------------------------------


@login_required
def owner_pet_list(request):
    guard = _require_pet_owner(request)
    if guard:
        return guard

    pet_owner = get_object_or_404(PetOwner, user=request.user)

    # Only show active (non-archived) pets
    pets = Pet.objects.filter(owner=pet_owner, is_archived=False)

    # Check which pets have a pending deletion request
    # Used in template to show the "Pending deletion" badge
    pending_deletion_pks = set(
        PetDeletionRequest.objects.filter(
            pet__in=pets,
            status=PetDeletionRequest.PENDING,
        ).values_list("pet_id", flat=True)
    )

    return render(
        request,
        "owner/pets/list.html",
        {
            "pets": pets,
            "pending_deletion_pks": pending_deletion_pks,
        },
    )


# ---------------------------------------------------------------------------
# Pets — Detail
# ---------------------------------------------------------------------------


@login_required
def owner_pet_detail(request, pk):
    guard = _require_pet_owner(request)
    if guard:
        return guard

    pet_owner = get_object_or_404(PetOwner, user=request.user)

    # Ensure the pet belongs to this owner
    pet = get_object_or_404(Pet, pk=pk, owner=pet_owner, is_archived=False)

    # Check for a pending deletion request on this pet
    pending_deletion = PetDeletionRequest.objects.filter(
        pet=pet,
        status=PetDeletionRequest.PENDING,
    ).first()

    return render(
        request,
        "owner/pets/detail.html",
        {
            "pet": pet,
            "pending_deletion": pending_deletion,
        },
    )


# ---------------------------------------------------------------------------
# Pets — Add
# ---------------------------------------------------------------------------


@login_required
def owner_pet_add(request):
    guard = _require_pet_owner(request)
    if guard:
        return guard

    pet_owner = get_object_or_404(PetOwner, user=request.user)

    if request.method == "POST":
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = pet_owner
            pet.save()
            messages.success(request, f"{pet.name} has been added.")
            return redirect("owner_pet_detail", pk=pet.pk)

    else:
        form = PetForm()

    return render(
        request,
        "owner/pets/add.html",
        {
            "form": form,
        },
    )


# ---------------------------------------------------------------------------
# Pets — Edit
# ---------------------------------------------------------------------------


@login_required
def owner_pet_edit(request, pk):
    guard = _require_pet_owner(request)
    if guard:
        return guard

    pet_owner = get_object_or_404(PetOwner, user=request.user)
    pet = get_object_or_404(Pet, pk=pk, owner=pet_owner, is_archived=False)

    # Block editing if a deletion request is pending
    pending_deletion = PetDeletionRequest.objects.filter(
        pet=pet,
        status=PetDeletionRequest.PENDING,
    ).first()
    if pending_deletion:
        messages.warning(
            request,
            "You cannot edit a pet while a deletion request is pending.",
        )
        return redirect("owner_pet_detail", pk=pet.pk)

    if request.method == "POST":
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f"{pet.name} has been updated.")
            return redirect("owner_pet_detail", pk=pet.pk)

    else:
        form = PetForm(instance=pet)

    return render(
        request,
        "owner/pets/edit.html",
        {
            "form": form,
            "pet": pet,
        },
    )


# ---------------------------------------------------------------------------
# Pets — Deletion Request
# ---------------------------------------------------------------------------


@login_required
def owner_pet_delete_request(request, pk):
    guard = _require_pet_owner(request)
    if guard:
        return guard

    pet_owner = get_object_or_404(PetOwner, user=request.user)
    pet = get_object_or_404(Pet, pk=pk, owner=pet_owner, is_archived=False)

    # Prevent duplicate pending requests
    existing_request = PetDeletionRequest.objects.filter(
        pet=pet,
        status=PetDeletionRequest.PENDING,
    ).first()
    if existing_request:
        messages.warning(
            request,
            "A deletion request for this pet is already pending.",
        )
        return redirect("owner_pet_detail", pk=pet.pk)

    if request.method == "POST":
        form = PetDeletionRequestForm(request.POST)
        if form.is_valid():
            deletion_request = form.save(commit=False)
            deletion_request.pet = pet
            deletion_request.requested_by = request.user
            deletion_request.status = PetDeletionRequest.PENDING
            deletion_request.save()
            messages.success(
                request,
                f"Deletion request for {pet.name} has been submitted. "
                "The clinic will review your request.",
            )
            return redirect("owner_pet_detail", pk=pet.pk)

    else:
        form = PetDeletionRequestForm()

    return render(
        request,
        "owner/pets/delete_request.html",
        {
            "form": form,
            "pet": pet,
        },
    )


# ---------------------------------------------------------------------------
# Pets — Cancel Deletion Request
# ---------------------------------------------------------------------------


@login_required
def owner_pet_cancel_delete_request(request, pk):
    guard = _require_pet_owner(request)
    if guard:
        return guard

    pet_owner = get_object_or_404(PetOwner, user=request.user)
    pet = get_object_or_404(Pet, pk=pk, owner=pet_owner, is_archived=False)

    # Only allow cancelling PENDING requests
    deletion_request = get_object_or_404(
        PetDeletionRequest,
        pet=pet,
        requested_by=request.user,
        status=PetDeletionRequest.PENDING,
    )

    # Only process on POST — prevents accidental cancellation via GET
    if request.method == "POST":
        deletion_request.delete()
        messages.success(
            request,
            f"Deletion request for {pet.name} has been cancelled.",
        )

    return redirect("owner_pet_detail", pk=pet.pk)