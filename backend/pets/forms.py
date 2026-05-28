# pets/forms.py

from django import forms
from django.forms import formset_factory

from .models import ContactLink, Pet, PetOwner

from .models import ContactLink, Pet, PetDeletionRequest, PetOwner


class PetOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = PetOwner
        fields = [
            "first_name",
            "last_name",
            "contact_number",
            "address_line",
            "barangay",
            "city_municipality",
            "province",
            "profile_photo",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "contact_number": forms.TextInput(
                attrs={"placeholder": "e.g. 09171234567"}
            ),
            "address_line": forms.TextInput(
                attrs={"placeholder": "e.g. Purok IV, Alihugon (optional)"}
            ),
            "barangay": forms.TextInput(attrs={"placeholder": "e.g. Amoingon"}),
            "city_municipality": forms.TextInput(attrs={"placeholder": "e.g. Baoc"}),
            "province": forms.TextInput(attrs={"placeholder": "e.g. Marinduque"}),
        }

    def clean_first_name(self):
        value = self.cleaned_data.get("first_name", "").strip()
        if not value:
            raise forms.ValidationError("First name is required.")
        return value.title()

    def clean_last_name(self):
        value = self.cleaned_data.get("last_name", "").strip()
        if not value:
            raise forms.ValidationError("Last name is required.")
        return value.title()

    def clean_address_line(self):
        value = self.cleaned_data.get("address_line", "").strip()
        # Preserve user casing but collapse extra whitespace
        return " ".join(value.split())

    def clean_barangay(self):
        value = self.cleaned_data.get("barangay", "").strip()
        return value.title()

    def clean_city_municipality(self):
        value = self.cleaned_data.get("city_municipality", "").strip()
        return value.title()

    def clean_province(self):
        value = self.cleaned_data.get("province", "").strip()
        return value.title()


class ContactLinkForm(forms.ModelForm):
    class Meta:
        model = ContactLink
        fields = ["platform", "url_or_handle"]
        widgets = {
            "platform": forms.TextInput(
                attrs={"placeholder": "Platform (e.g. Facebook)"}
            ),
            "url_or_handle": forms.TextInput(attrs={"placeholder": "URL or username"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        platform = cleaned_data.get("platform", "").strip()
        url_or_handle = cleaned_data.get("url_or_handle", "").strip()

        # Both fields must be filled together, or both left blank.
        # A row with only one field filled is invalid.
        if bool(platform) != bool(url_or_handle):
            raise forms.ValidationError(
                "Please fill in both the platform name and the URL or handle."
            )

        return cleaned_data

    def is_empty(self):
        """Returns True if both fields are blank — used to skip saving."""
        platform = self.cleaned_data.get("platform", "").strip()
        url_or_handle = self.cleaned_data.get("url_or_handle", "").strip()
        return not platform and not url_or_handle


# Two blank rows shown by default — extras left blank are skipped
ContactLinkFormSet = formset_factory(
    ContactLinkForm,
    extra=2,
    max_num=10,
    validate_max=True,
)


class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            "name",
            "species",
            "breed",
            "color",
            "gender",
            "date_of_birth",
            "weight",
            "registration_number",
            "photo",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Pet's name"}),
            # NOTE for frontend teammate:
            # species and breed are plain text inputs for now.
            # Phase 7 will upgrade these to a cascading dropdown with HTMX.
            # Do not wire up JS dropdowns yet — keep as text inputs.
            "species": forms.TextInput(attrs={"placeholder": "e.g. Dog, Cat, Bird"}),
            "breed": forms.TextInput(
                attrs={"placeholder": "e.g. Aspin, Persian (optional)"}
            ),
            "color": forms.TextInput(
                attrs={"placeholder": "e.g. Brown and white (optional)"}
            ),
            "gender": forms.Select(),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "weight": forms.NumberInput(
                attrs={"placeholder": "Weight in kg (optional)", "step": "0.01"}
            ),
            "registration_number": forms.TextInput(
                attrs={"placeholder": "Government-issued number (optional)"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # date_of_birth is optional in the model — reflect that in the form
        self.fields["date_of_birth"].required = False
        # Explicitly mark optional fields so the template can label them clearly
        self.fields["breed"].required = False
        self.fields["color"].required = False
        self.fields["weight"].required = False
        self.fields["registration_number"].required = False
        self.fields["photo"].required = False

    def clean_name(self):
        value = self.cleaned_data.get("name", "").strip()
        if not value:
            raise forms.ValidationError("Pet name is required.")
        return value

    def clean_species(self):
        value = self.cleaned_data.get("species", "").strip()
        if not value:
            raise forms.ValidationError("Species is required.")
        return value

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Weight must be greater than 0.")
        return weight

    def clean_date_of_birth(self):
        from django.utils import timezone

        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.now().date():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob


class PetDeletionRequestForm(forms.ModelForm):
    class Meta:
        model = PetDeletionRequest
        fields = ["reason", "reason_detail"]
        widgets = {
            "reason": forms.Select(),
            "reason_detail": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Please describe the reason (required if Other is selected)",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        reason = cleaned_data.get("reason")
        reason_detail = cleaned_data.get("reason_detail", "").strip()

        # If reason is OTHER, detail is required
        if reason == PetDeletionRequest.OTHER and not reason_detail:
            raise forms.ValidationError(
                "Please provide details when selecting Other as the reason."
            )

        return cleaned_data


class AdminPetOwnerForm(forms.ModelForm):
    """
    Used by Admin to manually create or edit a pet owner account.
    Does not include user account fields (email, password) —
    those are handled separately during walk-in creation in Phase 2.5.
    """

    class Meta:
        model = PetOwner
        fields = [
            "first_name",
            "last_name",
            "contact_number",
            "address_line",
            "barangay",
            "city_municipality",
            "province",
            "profile_photo",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "contact_number": forms.TextInput(
                attrs={"placeholder": "e.g. 09171234567"}
            ),
            "address_line": forms.TextInput(
                attrs={"placeholder": "e.g. Purok IV, Alihugon (optional)"}
            ),
            "barangay": forms.TextInput(attrs={"placeholder": "e.g. Amoingon"}),
            "city_municipality": forms.TextInput(attrs={"placeholder": "e.g. Boac"}),
            "province": forms.TextInput(attrs={"placeholder": "e.g. Marinduque"}),
        }

    def clean_first_name(self):
        value = self.cleaned_data.get("first_name", "").strip()
        if not value:
            raise forms.ValidationError("First name is required.")
        return value.title()

    def clean_last_name(self):
        value = self.cleaned_data.get("last_name", "").strip()
        if not value:
            raise forms.ValidationError("Last name is required.")
        return value.title()

    def clean_address_line(self):
        value = self.cleaned_data.get("address_line", "").strip()
        return " ".join(value.split())

    def clean_barangay(self):
        value = self.cleaned_data.get("barangay", "").strip()
        return value.title()

    def clean_city_municipality(self):
        value = self.cleaned_data.get("city_municipality", "").strip()
        return value.title()

    def clean_province(self):
        value = self.cleaned_data.get("province", "").strip()
        return value.title()


class AdminPetForm(forms.ModelForm):
    """
    Used by Admin to manually add or edit a pet.
    Includes all pet fields — Admin has full access unlike pet owners
    who can only edit minor details.
    """

    class Meta:
        model = Pet
        fields = [
            "name",
            "species",
            "breed",
            "color",
            "gender",
            "date_of_birth",
            "weight",
            "registration_number",
            "photo",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Pet's name"}),
            "species": forms.TextInput(attrs={"placeholder": "e.g. Dog, Cat, Bird"}),
            "breed": forms.TextInput(
                attrs={"placeholder": "e.g. Aspin, Persian (optional)"}
            ),
            "color": forms.TextInput(
                attrs={"placeholder": "e.g. Brown and white (optional)"}
            ),
            "gender": forms.Select(),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "weight": forms.NumberInput(
                attrs={
                    "placeholder": "Weight in kg (optional)",
                    "step": "0.01",
                }
            ),
            "registration_number": forms.TextInput(
                attrs={"placeholder": "Government-issued number (optional)"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_of_birth"].required = False
        self.fields["breed"].required = False
        self.fields["color"].required = False
        self.fields["weight"].required = False
        self.fields["registration_number"].required = False
        self.fields["photo"].required = False

    def clean_name(self):
        value = self.cleaned_data.get("name", "").strip()
        if not value:
            raise forms.ValidationError("Pet name is required.")
        return value.title()

    def clean_species(self):
        value = self.cleaned_data.get("species", "").strip()
        if not value:
            raise forms.ValidationError("Species is required.")
        return value.title()

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Weight must be greater than 0.")
        return weight

    def clean_date_of_birth(self):
        from django.utils import timezone

        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.now().date():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob
