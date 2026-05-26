# CONVENTIONS.md — Hapi Vet Code Conventions

> This file defines all coding conventions for Hapi Vet.
> Follow these rules consistently across all development.
> Update this file if conventions change mid-development.
> Both backend and frontend teammates must follow these rules.

---

## 1. Repository & Project Structure

```
Hapi-Thoughts/                  ← GitHub repo root
├── backend/                    ← entire Django project lives here
│   ├── hapivet/                ← Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── accounts/               ← user auth and onboarding
│   ├── pets/                   ← pet owners and pets
│   ├── appointments/           ← scheduling and booking
│   ├── medical/                ← medical records and vaccinations
│   ├── billing/                ← services, receipts, billing
│   ├── notifications/          ← in-app and email notifications
│   ├── health/                 ← health library articles
│   ├── dashboard/              ← admin and pet owner dashboard views
│   ├── templates/              ← all HTML templates (centralized)
│   ├── static/                 ← all static files (centralized)
│   ├── media/                  ← uploaded files (runtime, never commit)
│   ├── venv/                   ← virtual environment (never commit)
│   ├── .env                    ← environment variables (never commit)
│   ├── .env.example            ← example env file (safe to commit)
│   ├── requirements.txt        ← Python dependencies
│   └── manage.py
├── docs/                       ← all project documentation
│   ├── BRIEF.md
│   ├── STACK.md
│   ├── FEATURES.md
│   ├── DATA_MODELS.md
│   ├── CONVENTIONS.md
│   └── SYSTEM_INSTRUCTIONS.md
└── mobile/                     ← placeholder, unused in v1
```

> The repo is named `Hapi-Thoughts` — this is intentional and does not
> affect the Django project name (`hapivet`) or any code.
> Repo name and Django project name are completely separate.

> All Django commands are run from inside `backend/`:
> ```bash
> cd backend
> python manage.py runserver
> ```

> On Render, set the root directory to `backend/` in deployment settings.

---

## 2. Django App Structure

All apps live inside `backend/`. Each app follows this consistent internal structure.

> **Special case — `dashboard` app:**
> The dashboard app has no models of its own.
> It only contains views that pull and aggregate data from other apps.
> It handles the admin dashboard home and pet owner dashboard home exclusively.

```
app_name/
├── migrations/
├── templates/          ← NOT used (all templates centralized)
├── __init__.py
├── admin.py            ← Minimal — we use custom dashboard
├── apps.py
├── forms.py            ← All forms for this app
├── models.py           ← All models for this app
├── urls.py             ← URL patterns for this app
├── views.py            ← All views for this app
├── utils.py            ← Helper functions (if needed)
├── signals.py          ← Django signals (if needed)
└── tests.py
```

If `views.py` or `forms.py` grows too large, split into a folder:
```
views/
  ├── __init__.py
  ├── admin_views.py
  └── owner_views.py
```

---

## 3. Template Structure

All templates live in the top-level `templates/` folder.
Never use per-app template folders.

```
templates/
├── base.html                   ← Shared base template
├── shared/                     ← Shared components
│   ├── navbar.html
│   ├── sidebar_admin.html
│   ├── sidebar_owner.html
│   ├── modals.html
│   ├── flash_messages.html
│   └── pagination.html
├── admin/                      ← All admin-facing templates
│   ├── dashboard/
│   │   └── index.html
│   ├── appointments/
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── calendar.html
│   ├── pets/
│   │   ├── owners_list.html
│   │   ├── owner_detail.html
│   │   ├── pets_list.html
│   │   └── pet_detail.html
│   ├── medical/
│   │   ├── record_detail.html
│   │   └── record_form.html
│   ├── billing/
│   │   ├── receipt_list.html
│   │   ├── receipt_detail.html
│   │   └── services_list.html
│   ├── notifications/
│   │   └── index.html
│   ├── health/
│   │   ├── article_list.html
│   │   └── article_form.html
│   └── settings/
│       └── clinic_settings.html
└── owner/                      ← All pet owner-facing templates
    ├── dashboard/
    │   └── index.html
    ├── appointments/
    │   ├── list.html
    │   ├── book.html
    │   └── detail.html
    ├── pets/
    │   ├── list.html
    │   ├── detail.html
    │   └── add.html
    ├── medical/
    │   └── history.html
    ├── billing/
    │   ├── list.html
    │   └── receipt_detail.html
    ├── notifications/
    │   └── index.html
    ├── health/
    │   ├── article_list.html
    │   └── article_detail.html
    └── profile/
        ├── index.html
        └── edit.html
```

---

## 4. Static Files Structure

All static files live in the top-level `static/` folder.

```
static/
├── css/
│   ├── admin/              ← Admin-specific styles
│   └── owner/              ← Pet owner-specific styles
├── js/
│   ├── admin/              ← Admin-specific scripts
│   └── owner/              ← Pet owner-specific scripts
└── images/
    ├── clinic/             ← Clinic logo and branding
    └── defaults/           ← Default avatars and placeholders
```

### Media files (user uploads)
```
media/
├── clinic/                 ← Clinic logo uploads
├── owners/                 ← Pet owner profile photos
├── pets/                   ← Pet profile photos
└── test_results/           ← Medical test result files
```

> `media/` is generated at runtime — never commit it to GitHub.
> Add `media/` to `.gitignore`.

---

## 5. URL Structure

### Role-prefixed URL pattern
All URLs are prefixed by role for clear separation.

```
/                           ← Landing / login redirect
/login/                     ← Pet Owner login
/register/                  ← Pet Owner registration
/admin-login/               ← Admin login (separate)

/owner/dashboard/           ← Pet Owner dashboard
/admin/dashboard/           ← Admin dashboard
/owner/pets/                ← Pet list
/owner/pets/<id>/           ← Pet detail
/owner/appointments/        ← Appointment list
/owner/appointments/book/   ← Book appointment
/owner/profile/             ← Profile page
/owner/billing/             ← Billing history
/owner/notifications/       ← Notifications
/owner/health/              ← Health library

/admin/appointments/        ← Appointment management
/admin/pets/                ← Pet owner and pet management
/admin/medical/             ← Medical records
/admin/billing/             ← Billing management
/admin/services/            ← Service catalog
/admin/notifications/       ← Notification management
/admin/health/              ← Health library management
/admin/settings/            ← Clinic settings
```

### URL naming convention
URL names follow the pattern: `role:app_action`

```python
# accounts/urls.py
path('login/', views.login_view, name='owner_login'),
path('register/', views.register_view, name='owner_register'),

# appointments/urls.py — owner
path('owner/appointments/', views.appointment_list, name='owner_appointments'),
path('owner/appointments/book/', views.book_appointment, name='owner_book_appointment'),
path('owner/appointments/<int:pk>/', views.appointment_detail, name='owner_appointment_detail'),

# appointments/urls.py — admin
path('admin/appointments/', views.admin_appointment_list, name='admin_appointments'),
path('admin/appointments/<int:pk>/approve/', views.approve_appointment, name='admin_approve_appointment'),
```

### Main urls.py includes all app urls
```python
# hapivet/urls.py
urlpatterns = [
    path('', include('accounts.urls')),
    path('owner/', include('pets.urls')),
    path('owner/', include('appointments.urls')),
    path('admin/', include('appointments.urls')),
    path('admin/', include('medical.urls')),
    path('admin/', include('billing.urls')),
    # etc.
]
```

---

## 6. Naming Conventions

### Python / Django
| Item | Convention | Example |
|---|---|---|
| Files | snake_case | `pet_forms.py`, `appointment_utils.py` |
| Variables | snake_case | `pet_owner`, `appointment_date` |
| Functions | snake_case | `get_available_slots()`, `send_reminder_email()` |
| Classes | PascalCase | `PetOwner`, `AppointmentForm` |
| Constants | UPPER_SNAKE_CASE | `MAX_BOOKING_DAYS`, `DEFAULT_SLOT_DURATION` |
| Model fields | snake_case | `date_of_birth`, `is_archived` |
| URL names | snake_case with role prefix | `owner_appointments`, `admin_approve_appointment` |
| Template names | snake_case | `appointment_list.html`, `pet_detail.html` |

### HTML / Templates
| Item | Convention | Example |
|---|---|---|
| Template variables | snake_case | `{{ pet_owner.first_name }}` |
| Block names | snake_case | `{% block page_content %}` |
| Template tags | snake_case | `{% url 'owner_appointments' %}` |
| CSS classes | Tailwind utility classes only | `class="flex items-center gap-4"` |
| Custom CSS classes | kebab-case | `class="appointment-card"` |
| HTMX attributes | standard htmx attributes | `hx-get`, `hx-target`, `hx-trigger` |

---

## 7. View Conventions

All views are **function-based**. No class-based views.

### Standard view structure
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment

@login_required
def appointment_list(request):
    # 1. Permission check
    if request.user.role != 'pet_owner':
        return redirect('admin_dashboard')

    # 2. Query data
    appointments = Appointment.objects.filter(
        owner=request.user.petowner
    ).order_by('-date')

    # 3. Handle POST
    if request.method == 'POST':
        # form handling logic
        pass

    # 4. Return response
    return render(request, 'owner/appointments/list.html', {
        'appointments': appointments,
    })
```

### HTMX views (partial responses)
HTMX views return partial HTML, not full pages.
Use a naming convention to distinguish them:

```python
def appointment_list_partial(request):
    """Returns partial HTML for HTMX polling updates."""
    appointments = Appointment.objects.filter(...)
    return render(request, 'owner/appointments/_list_partial.html', {
        'appointments': appointments,
    })
```

Partial templates are prefixed with underscore: `_list_partial.html`

### Role protection
Always check role at the top of every view:

```python
@login_required
def admin_only_view(request):
    if request.user.role != 'admin':
        return redirect('owner_dashboard')
    # rest of view
```

---

## 8. Model Conventions

### Field ordering in models
Always define fields in this order:
1. Primary key (if custom)
2. ForeignKey / OneToOneField relationships
3. Core data fields
4. Status / boolean flags
5. Timestamps (`created_at`, `updated_at`)

### Standard model template
```python
from django.db import models

class Appointment(models.Model):

    # 1. Status choices defined at top of class
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (NO_SHOW, 'No Show'),
    ]

    # 2. Relationships
    owner = models.ForeignKey('pets.PetOwner', on_delete=models.CASCADE)
    pet = models.ForeignKey('pets.Pet', on_delete=models.CASCADE)
    service = models.ForeignKey('billing.Service', on_delete=models.SET_NULL, null=True)

    # 3. Core fields
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    # 4. Flags
    is_walk_in = models.BooleanField(default=False)

    # 5. Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 6. Meta
    class Meta:
        ordering = ['-date', '-time']

    # 7. String representation
    def __str__(self):
        return f"{self.pet.name} — {self.date} {self.time}"

    # 8. Properties / helper methods
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.date >= timezone.now().date()
```

---

## 9. Form Conventions

All forms live in `forms.py` within their app.
Use Django ModelForms wherever possible.

```python
from django import forms
from .models import Appointment

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'date', 'time', 'service', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        # validation logic here
        return cleaned_data
```

---

## 10. Template Conventions

### Base template structure
Every page extends `base.html`:
```html
{% extends 'base.html' %}

{% block title %}Appointments — Hapi Vet{% endblock %}

{% block page_content %}
  <!-- page content here -->
{% endblock %}
```

### Base template blocks
```html
<!-- base.html -->
{% block title %}Hapi Vet{% endblock %}
{% block extra_css %}{% endblock %}    ← page-specific CSS
{% block content %}{% endblock %}      ← full page content
{% block page_content %}{% endblock %} ← main content area only
{% block extra_js %}{% endblock %}     ← page-specific JS
```

### HTMX partial templates
Partials are prefixed with underscore and never extend base.html:
```
_list_partial.html      ← table or list update
_notification_count.html ← badge count update
_calendar_day.html       ← calendar day update
```

### Template variable naming
Always use descriptive context variable names:
```python
# Good
return render(request, 'template.html', {
    'appointments': appointments,
    'pending_count': pending_count,
    'selected_pet': pet,
})

# Avoid
return render(request, 'template.html', {
    'data': appointments,
    'count': pending_count,
    'obj': pet,
})
```

---

## 11. Tailwind CSS Conventions

### Phase 1 (CDN) — current
```html
<script src="https://cdn.tailwindcss.com"></script>
```
Use standard Tailwind utility classes only.
No custom config in Phase 1.

### Class ordering convention
Follow this order for Tailwind classes:
```
Layout → Sizing → Spacing → Typography → Colors → Borders → Effects
```

Example:
```html
<div class="flex items-center w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50">
```

### Color usage
Until Figma design is finalized, use neutral Tailwind colors:
- Primary actions: `blue-600`
- Danger/delete: `red-600`
- Success: `green-600`
- Warning: `yellow-500`
- Neutral: `gray-*`

These will be replaced with clinic brand colors when Figma is ready.

### Status badge convention
Appointment and billing statuses use consistent color badges:
```html
<!-- Pending -->
<span class="px-2 py-1 text-xs font-medium text-yellow-700 bg-yellow-100 rounded-full">
  Pending
</span>

<!-- Confirmed -->
<span class="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full">
  Confirmed
</span>

<!-- Completed -->
<span class="px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full">
  Completed
</span>

<!-- Cancelled -->
<span class="px-2 py-1 text-xs font-medium text-red-700 bg-red-100 rounded-full">
  Cancelled
</span>

<!-- No Show -->
<span class="px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
  No Show
</span>
```

---

## 12. Code Style — Black + Flake8

### What they do
- **Black** — auto-formats Python code consistently on save
- **Flake8** — checks for errors, bad practices, and style issues

### Installation
```bash
pip install black flake8
```

Add to `requirements.txt`:
```
black
flake8
```

### VS Code setup
Add to `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=88"],
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### Flake8 config
Add `.flake8` file to project root:
```ini
[flake8]
max-line-length = 88
exclude =
    migrations,
    .git,
    __pycache__,
    .env
ignore = E203, W503
```

### Rules
- Black formats automatically on save — never manually adjust spacing
- Fix all Flake8 warnings before committing
- Never commit code with linting errors
- Both teammates should have same VS Code settings

---

## 13. Git Conventions

### Branch naming
```
main              ← stable, production-ready
rebuild           ← active clean rebuild
feature/auth      ← new feature
feature/appointments
feature/medical-records
fix/login-redirect
fix/slot-conflict
```

### Commit message format
```
type: short description

Examples:
feat: add appointment booking form
fix: correct slot conflict validation
model: add is_corrected field to Vaccination
style: format views.py with black
docs: update DATA_MODELS.md with TestResultFile changes
```

### Commit types
| Type | When to use |
|---|---|
| `feat` | New feature added |
| `fix` | Bug fixed |
| `model` | Model or migration change |
| `style` | Code formatting only |
| `docs` | Documentation update |
| `refactor` | Code restructured, no behavior change |
| `test` | Tests added or updated |

### Rules
- Never commit directly to `main`
- Always work on a feature branch
- Update relevant md files in the same commit as the code change
- Never commit `backend/.env`
- Never commit `backend/media/` folder
- Never commit `backend/venv/` folder
- Never commit `backend/db.sqlite3`
- Run Black and Flake8 before every commit

---

## 14. Environment Variables

### File locations
```
backend/.env            ← actual env values (never commit)
backend/.env.example    ← template with empty values (safe to commit)
```

### .env file (never commit)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/hapivet_db
EMAIL_HOST_USER=hapitutzvet@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
ALLOWED_HOSTS=localhost,127.0.0.1
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### .env.example (safe to commit)
```env
SECRET_KEY=
DEBUG=
DATABASE_URL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
ALLOWED_HOSTS=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

Always update `.env.example` when adding new environment variables.

---

## 15. Quick Reference Checklist

Before starting any feature:
- [ ] Check `FEATURES.md` for the feature scope
- [ ] Check `DATA_MODELS.md` for the relevant models

Before committing:
- [ ] Black formatting applied
- [ ] Flake8 has no errors
- [ ] Relevant md files updated if models or features changed
- [ ] `.env` not included in commit
- [ ] Working on a feature branch, not `main`

Before changing a model:
- [ ] Update `DATA_MODELS.md` first
- [ ] Run `makemigrations` and `migrate`
- [ ] Update `FEATURES.md` if feature scope changed
