# EduFlow — Product North Star

## 1. Mission
EduFlow is a student admissions and document workflow platform initially designed around the real enrollment process at Motion Web IT Academy in Kyrgyzstan.
Goal: Build a credible, working, demo-ready product for a hackathon.

## 2. Core Product Promise
"Enter student information once. Validate it, prepare approved documents, and track the admission process in one place."

## 3. Initial Target Institution: Motion Web IT Academy
Simplified enrollment workflow:
- Student enters application.
- Student provides identity document for verification.
- Institution and student enter into a course contract.
- Payment is handled and confirmed according to actual institution process.

## 4. MVP Priorities (P0)
1. Student application form with server-side validation.
2. Institution/program-specific requirements.
3. Application persistence in PostgreSQL.
4. Application status timeline (DRAFT -> SUBMITTED -> UNDER_REVIEW -> NEEDS_CORRECTION -> APPROVED -> DOCUMENT_READY -> ENROLLED).
5. Administrator authentication and authorization.
6. Admin application list, filters, and status actions.
7. Approved/demo template document generation (Jinja2 + WeasyPrint).
8. Protected document access (no public downloads).
9. Reproducible Docker startup and migrations.
10. Synthetic demo data and repeatable demo scenario.

## 5. Security & Privacy
- Administrator endpoints require JWT/session auth.
- No public access to other applicants' records.
- Synthetic demo data only; no real passport copies or personal numbers.
- Unapproved templates visibly marked: "DEMO — NOT A LEGAL DOCUMENT — NOT FOR SIGNING".
