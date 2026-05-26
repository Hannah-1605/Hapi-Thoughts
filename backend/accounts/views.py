from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

User = None  # loaded lazily via get_user_model()


def get_user_model_lazy():
    from django.contrib.auth import get_user_model
    return get_user_model()


# ─── Role-based redirect helper ───────────────────────────────────────────────

def redirect_by_role(user):
    """Redirect user to the correct dashboard based on their role."""
    if user.role == "admin":
        return redirect("admin_dashboard")
    return redirect("owner_dashboard")


# ─── Pet Owner Login ──────────────────────────────────────────────────────────

def owner_login(request):
    """Login page for pet owners."""
    # Already logged in — redirect to correct dashboard
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # Django's authenticate expects username field — we pass email as username
        # because our User model uses email as the unique identifier
        User = get_user_model_lazy()
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, "owner/login.html", {"email": email})

        if user.role != "pet_owner":
            messages.error(request, "Please use the admin login page.")
            return render(request, "owner/login.html", {"email": email})

        if not user.is_active:
            messages.error(request, "Your account has been deactivated. Please contact the clinic.")
            return render(request, "owner/login.html", {"email": email})

        login(request, user)

        # Redirect to onboarding if not yet completed
        if not user.is_onboarded:
            return redirect("owner_onboarding")

        return redirect("owner_dashboard")

    return render(request, "owner/login.html")


# ─── Admin Login ──────────────────────────────────────────────────────────────

def admin_login(request):
    """Separate login page for admin only."""
    # Already logged in — redirect to correct dashboard
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        User = get_user_model_lazy()
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is None:
            messages.error(request, "Invalid email or password.")
            return render(request, "admin/login.html", {"email": email})

        if user.role != "admin":
            messages.error(request, "You do not have admin access.")
            return render(request, "admin/login.html", {"email": email})

        if not user.is_active:
            messages.error(request, "This account has been deactivated.")
            return render(request, "admin/login.html", {"email": email})

        login(request, user)
        return redirect("admin_dashboard")

    return render(request, "admin/login.html")


# ─── Logout ───────────────────────────────────────────────────────────────────

@login_required
def user_logout(request):
    """Logs out any user and redirects to pet owner login."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("owner_login")


# ─── Placeholder Dashboards ───────────────────────────────────────────────────
# These are temporary — replaced in Phase 7 with full dashboard views

@login_required
def admin_dashboard(request):
    """Placeholder admin dashboard."""
    if request.user.role != "admin":
        return redirect("owner_dashboard")
    return render(request, "admin/dashboard/index.html")


@login_required
def owner_dashboard(request):
    """Placeholder pet owner dashboard."""
    if request.user.role != "pet_owner":
        return redirect("admin_dashboard")

    # Redirect to onboarding if not completed
    if not request.user.is_onboarded:
        return redirect("owner_onboarding")

    return render(request, "owner/dashboard/index.html")


@login_required
def owner_onboarding(request):
    """Placeholder onboarding view — built properly in Phase 2."""
    if request.user.role != "pet_owner":
        return redirect("admin_dashboard")
    return render(request, "owner/onboarding.html")

def owner_register(request):
    """Pet owner registration — built fully in Phase 1.2."""
    return render(request, "owner/register.html")