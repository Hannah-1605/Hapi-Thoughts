# BRIEF.md — Hapi Vet Project Overview

## 1. Project Identity

| Field | Value |
|---|---|
| **System Name** | Hapi Vet |
| **Full Name** | Hapi Vet Veterinary Clinic Management System |
| **Client** | Hapi Tutz Vet. Supplies |
| **Location** | Bognuyan, Gasan, Marinduque |
| **Clinic Owner / Veterinarian** | Dr. Edgar Sadiwa |
| **Version** | v1.0 |
| **Type** | Web-based Clinic Management System |

---

## 2. Project Context

Hapi Tutz Veterinary Clinic currently operates using paper-based records, manual
appointment scheduling, and phone-based client communication. This results in:

- Difficulty retrieving patient records
- Missed appointments due to no reminder system
- Inconsistent scheduling and double-bookings
- No centralized record of billing or medical history

Hapi Vet is a purpose-built digital solution to replace these manual processes with a
unified, user-friendly web application.

---

## 3. Core Purpose

Hapi Vet centralizes all clinic operations into one platform:

- Appointment scheduling with slot-based booking
- Digital pet medical records
- Vaccination tracking with reminders
- Billing and receipt generation
- In-app and email notifications for clients and admin

---

## 4. Who Uses the System

### Admin (Dr. Edgar Sadiwa)
The sole administrator of the system. Dr. Edgar is both the clinic owner and
veterinarian. He is the only user with write access to medical records, billing,
and appointment approvals.

> v1 is a **single admin model**. No staff or receptionist roles exist in this version.
> This is a known future expansion point — a `role` field can be added to the User
> model when clinic staff are hired.

### Pet Owners (Clients)
Registered clients of the clinic. They can book appointments, view their pets'
medical history (public notes only), and receive notifications and billing receipts
through their own dashboard.

---

## 5. System Scope

### Included in v1
- User authentication (Admin + Pet Owner)
- Pet Owner registration and profile management
- Pet management
- Slot-based appointment scheduling with Admin approval workflow
- Medical records (with public and private note layers)
- Vaccination tracking
- Billing and receipt generation
- Services and pricing management
- In-app and email notifications (Gmail SMTP)
- Admin dashboard
- Pet Owner dashboard
- AJAX/HTMX polling for near real-time updates (no WebSockets)

### Explicitly Out of Scope (v1)
- Online payment gateway (GCash, Stripe, PayPal)
- SMS notifications
- Real-time chat or messaging
- AI-based diagnosis or suggestions
- Multi-veterinarian scheduling
- Multi-clinic / multi-branch support
- Marketplace or e-commerce features
- Receptionist or staff role management

---

## 6. Core Business Rules

These rules are non-negotiable and must be enforced at the system level:

1. Each Pet belongs to exactly one Pet Owner
2. Appointments must go through Admin approval (PENDING → CONFIRMED)
3. Medical records are created and edited by Admin only
4. Medical records are immutable — no deletion allowed
5. Billing is generated only after an appointment is marked COMPLETED
6. Payment is handled externally (cash) — Admin records payment status manually
7. No double-booking — slot exclusivity is enforced by the system
8. Pet Owners can only view public notes on medical records
9. Private medical notes are visible to Admin only

---

## 7. Design Philosophy

> Hapi Vet is a single-clinic operational management system, not a platform.

All design and development decisions must prioritize:

- **Reliability** over complexity
- **Clarity** over premature scalability
- **Maintainability** over feature richness
- **Simplicity** — the system must be usable by non-technical clinic staff

---

## 8. Development Setup

| Item | Status |
|---|---|
| Framework | Django (Python) |
| Database | PostgreSQL (connected) |
| Styling | Tailwind CSS |
| Version Control | GitHub (repo exists) |
| Django running locally | Yes |
| Migrations applied | Yes |
| Starting point | Fresh rebuild on new branch (`rebuild` or `v2-clean`) |

---

## 9. Team Structure

| Role | Responsibility |
|---|---|
| Backend Lead (Project Leader) | Django models, views, URLs, business logic, database |
| Frontend | Tailwind CSS templates, UI components, Figma design |

### Collaboration Workflow
- Shared GitHub repository with branch-based workflow
- Backend sets up template HTML structure first
- Frontend applies Tailwind styling on top of backend templates
- `templates/` folder is the primary collaboration point
- Frontend design (Figma) is in progress — not yet finalized

---

## 10. Reference Documents

| File | Purpose |
|---|---|
| `BRIEF.md` | Project overview, goals, scope |
| `STACK.md` | Technical stack and configuration details |
| `FEATURES.md` | Full feature list with build order and status |
| `DATA_MODELS.md` | Django model definitions and relationships |
| `CONVENTIONS.md` | Code style, naming, and structure rules |
| `SYSTEM_INSTRUCTIONS.md` | Claude project instructions |
| `Project_Proposal.pdf` | UI mockups and original diagrams (reference only — superseded by md files) |

---

## 11. Key Constraint Reminder for AI Assistance

When working on this project:

- Treat the md files collectively as the **final authority**
- Do NOT introduce features outside the v1 scope
- Do NOT rename models or fields without explicit approval
- Do NOT suggest payment gateways, SMS, or AI features
- ALWAYS follow existing model definitions strictly
- ASK before changing database schema
