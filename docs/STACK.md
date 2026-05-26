# STACK.md — Hapi Vet Technical Stack

> This file defines the complete technical stack for Hapi Vet.
> All development decisions must align with this document.
> Update this file if any stack decision changes mid-development.

---

## 1. Core Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.10.11 |
| Framework | Django | 5.2.12 |
| Database | PostgreSQL | port 5432 |
| Styling | Tailwind CSS | CDN (Phase 1) → django-tailwind (Phase 2) |
| Template Engine | Django Templates | built-in |
| Frontend Interactivity | HTMX | latest CDN |
| Version Control | Git + GitHub | — |
| App Hosting | Render | free tier |
| Database Hosting | Supabase | free tier, permanent |
| Uptime Monitoring | UptimeRobot | free tier |

---

## 2. Database

- **Engine:** PostgreSQL
- **Host (local):** localhost, port 5432
- **Host (production):** Supabase (permanent free PostgreSQL, no expiry)
- **Connection:** via `DATABASE_URL` environment variable in all environments
- **ORM:** Django ORM (no raw SQL unless absolutely necessary)
- **Migrations:** Django migrations only — never modify the database directly

### Rules
- Always use `python manage.py makemigrations` and `migrate` for schema changes
- Never delete migration files
- Never modify an existing migration — create a new one instead
- Ask before changing any model schema mid-development

---

## 3. Tailwind CSS — Two Phase Plan

### Phase 1 (Current) — CDN
Tailwind is loaded via CDN in the base template. Used during backend
development to apply basic styling to templates without a build step.

```html
<script src="https://cdn.tailwindcss.com"></script>
```

No Node.js required. No build process. Quick to use.

**Limitation:** No custom config, no purging of unused CSS.
Acceptable for development — not for production.

### Phase 2 — django-tailwind (Frontend Integration)
When the frontend teammate's Figma design is finalized, the project
migrates to `django-tailwind` for:

- Full `tailwind.config.js` customization
- Custom color palette and spacing from Figma design system
- CSS purging for production builds
- Proper component class definitions

**Trigger for Phase 2:** Frontend Figma design finalized + teammate ready to integrate.

---

## 4. Django Configuration

### Admin Dashboard
- Django's built-in `/admin` is **disabled / not used**
- A fully custom admin dashboard is built using regular Django views
- This gives full control over layout, styling, and UX

### Apps Structure (planned)
```
hapivet/              ← Django project root
├── core/             ← shared utilities, base models, context processors
├── accounts/         ← custom user model, authentication
├── pets/             ← pet owner and pet management
├── appointments/     ← slot generation, booking, approval workflow
├── medical/          ← medical records, vaccination tracking
├── billing/          ← services, pricing, receipts
├── notifications/    ← in-app and email notifications
└── dashboard/        ← admin and pet owner dashboard views
```

> App structure may be adjusted as development progresses.
> Update this file if apps are added, renamed, or merged.

### Custom User Model
- Uses a custom `AbstractUser` model in the `accounts` app
- Must be defined **before** the first migration
- `AUTH_USER_MODEL = 'accounts.User'`
- Role field: `ADMIN` or `PET_OWNER`

---

## 5. Frontend Interactivity — HTMX

HTMX handles all dynamic UI updates without writing manual JavaScript.

### Use Cases in Hapi Vet
- Appointment table auto-refresh (polling)
- Notification badge updates
- Form submissions without full page reload
- Modal open/close interactions
- Inline status updates (appointment approve/reject)

### Polling Strategy
- Dashboard data refreshes every **10–30 seconds** via HTMX polling
- No WebSockets, no Django Channels, no Redis
- Partial HTML responses returned from Django views
- Only the relevant section of the page updates — not a full reload

### Loading via CDN
```html
<script src="https://unpkg.com/htmx.org@latest"></script>
```

---

## 6. Email — Gmail SMTP

### Configuration (settings.py)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  # Gmail App Password
```

### Development Email Account
- `hapitutzvet@gmail.com` (dedicated test account)
- Uses a Gmail App Password (not the account password)
- Stored in `.env` file — never hardcoded in source code

### Production Behavior
- Admin email is a **configurable system setting**
- Dr. Edgar enters his preferred notification email in the clinic settings
- All system notifications route to that configured address
- This means the email recipient is dynamic, not hardcoded

### Sending Strategy
- **Synchronous** — email sends immediately as part of the request
- No background workers (no Celery, no Django-Q)
- Acceptable for v1 given low clinic traffic volume

### Trigger Events
| Event | Recipient |
|---|---|
| Appointment requested | Admin |
| Appointment approved/rejected | Pet Owner |
| Appointment reminder | Pet Owner |
| Billing generated | Pet Owner |
| Vaccination due reminder | Pet Owner |
| Follow-up reminder | Pet Owner |

---

## 7. Environment Variables

All sensitive configuration is stored in a `.env` file.
Never commit `.env` to GitHub.

```env
SECRET_KEY=
DEBUG=
DATABASE_URL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
ALLOWED_HOSTS=
```

Use `django-environ` or `python-decouple` to load these in `settings.py`.

---

## 8. Key Dependencies (planned)

| Package | Purpose |
|---|---|
| `django` | core framework |
| `psycopg2-binary` | PostgreSQL adapter |
| `django-environ` or `python-decouple` | environment variable management |
| `pillow` | image handling (pet/owner profile photos) |
| `whitenoise` | static file serving in production |
| `gunicorn` | production WSGI server (required by Render) |

> Keep dependencies minimal. Do not add packages without a clear need.
> Update this list as packages are installed.

---

## 9. Deployment

### Architecture
| Service | Purpose | Cost |
|---|---|---|
| **Render** | Django app hosting | Free, permanent |
| **Supabase** | PostgreSQL database hosting | Free, permanent, no expiry |
| **UptimeRobot** | Prevents Render cold starts | Free |
| **GitHub** | Code repository + deploy trigger | Free |

### Why This Setup
- Render's free PostgreSQL expires after 30 days — so we use Supabase for the
  database instead, which has no expiry on its free tier
- Render hosts the Django app and deploys automatically on every push to `main`
- UptimeRobot pings the app every 10 minutes to prevent the 15-minute sleep
  (cold start) on Render's free tier
- Total cost: ₱0 with no expiry issues

### How They Connect
```
GitHub (code) → Render (Django app) → Supabase (PostgreSQL)
                      ↑
               UptimeRobot (keeps awake)
```

Django connects to Supabase via a standard PostgreSQL connection string —
no special Supabase SDK or library needed.

```env
DATABASE_URL=postgresql://user:password@db.supabase.co:5432/postgres
```

### Render Configuration
- **Deployment trigger:** push to `main` branch on GitHub
- **Static files:** served via WhiteNoise
- **Environment variables:** set in Render dashboard (not in code)
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn hapivet.wsgi`

### Deployment Checklist (when ready)
- [ ] `DEBUG = False` in production settings
- [ ] `ALLOWED_HOSTS` includes Render domain
- [ ] Static files configured with WhiteNoise
- [ ] `python manage.py collectstatic` runs on deploy
- [ ] `DATABASE_URL` set to Supabase connection string in Render dashboard
- [ ] Gmail App Password set in Render environment variables
- [ ] All migrations applied on Supabase database
- [ ] UptimeRobot configured to ping Render app URL every 10 minutes

---

## 10. Development Workflow

### Branch Strategy
| Branch | Purpose |
|---|---|
| `main` | stable, production-ready code |
| `rebuild` | current clean rebuild (active development) |
| `feature/xxx` | individual feature branches |

### Recommended Flow
1. Work on `feature/xxx` branch
2. Test locally
3. Merge into `rebuild` via pull request
4. When `rebuild` is stable, merge into `main` for deployment

### Frontend Collaboration
- Backend builds template HTML structure first (unstyled or basic CDN Tailwind)
- Frontend teammate applies Tailwind classes and component styling
- `templates/` folder is the primary collaboration point
- Coordinate before changing template file names or folder structure

---

## 11. What This Stack Does NOT Include

These are explicitly excluded from v1:

- WebSockets / Django Channels
- Redis or Celery
- Django REST Framework (no API — this is a server-rendered app)
- React, Vue, or any JS framework
- SMS gateway (Semaphore, Twilio)
- Payment gateway (GCash, Stripe, PayPal)
- Django built-in `/admin`
- Multi-tenancy or SaaS architecture
