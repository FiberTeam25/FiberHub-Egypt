# FiberHub Egypt — MVP Planning Document

## STEP 1: High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS                               │
│  Browser (Next.js SSR + CSR)  │  Admin Panel (same Next.js) │
└──────────────────┬──────────────────────────────┬────────────┘
                   │ HTTPS                        │
                   ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     NGINX / Reverse Proxy                    │
│              (SSL termination, static assets)                │
└──────────────────┬──────────────────────────────┬────────────┘
                   │                              │
        ┌──────────▼──────────┐        ┌──────────▼──────────┐
        │   Next.js Server    │        │   FastAPI Server     │
        │   (SSR + BFF)       │        │   (REST API)         │
        │   Port 3000         │        │   Port 8000          │
        └─────────────────────┘        └──────────┬───────────┘
                                                  │
                              ┌────────────────────┼────────────────┐
                              │                    │                │
                   ┌──────────▼───┐    ┌───────────▼──┐   ┌────────▼─────┐
                   │  PostgreSQL  │    │  S3 / MinIO   │   │  Redis       │
                   │  Port 5432   │    │  (file store)  │   │  (cache,     │
                   └──────────────┘    └──────────────┘   │   bg jobs)   │
                                                          └──────────────┘
                                                                │
                                                     ┌──────────▼──────────┐
                                                     │  Background Worker  │
                                                     │  (email, notifs)    │
                                                     └─────────────────────┘
```

### Architecture decisions

- **Modular monolith** — single backend, single frontend, cleanly separated modules
- **Next.js as BFF** — handles SSR, auth cookies, proxies API calls
- **FastAPI owns all business logic** — the frontend never touches the DB directly
- **Redis** — background job queue (arq) + optional response caching
- **MinIO** in dev, **S3** in prod — same API, seamless switch via env vars
- **PostgreSQL** full-text search — no Elasticsearch in MVP
- **Polling for messages** — no WebSockets in MVP (10-15s interval on active threads)

---

## STEP 2: Project Folder Structure

### Root

```
fiberhub-egypt/
├── backend/
├── frontend/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .gitignore
├── README.md
├── PLANNING.md
└── CLAUDE.md
```

### Backend (`/backend`)

```
backend/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory
│   ├── config.py                  # Settings from env vars (pydantic-settings)
│   ├── database.py                # Engine, session factory
│   ├── dependencies.py            # Shared FastAPI dependencies
│   ├── exceptions.py              # Custom exception classes + handlers
│   ├── middleware.py              # CORS, rate limiting, request logging
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py             # /api/v1/auth/* endpoints
│   │   ├── service.py            # Auth business logic
│   │   ├── schemas.py            # Pydantic request/response models
│   │   ├── utils.py              # JWT encode/decode, password hashing
│   │   └── dependencies.py       # get_current_user, require_role, etc.
│   │
│   ├── users/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── companies/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── profiles/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── categories/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── search/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── verification/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── rfqs/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── messages/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── reviews/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── repository.py
│   │
│   ├── models/                   # All SQLAlchemy models in one place
│   │   ├── __init__.py           # Re-exports all models for Alembic
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── profile.py
│   │   ├── category.py
│   │   ├── verification.py
│   │   ├── rfq.py
│   │   ├── message.py
│   │   ├── review.py
│   │   ├── notification.py
│   │   └── admin.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── s3.py                 # S3/MinIO upload, download, presigned URLs
│   │
│   └── workers/
│       ├── __init__.py
│       ├── email.py              # Email sending tasks
│       └── notifications.py      # Notification dispatch
│
├── tests/
│   ├── conftest.py               # Fixtures: test DB, test client, auth helpers
│   ├── test_auth/
│   ├── test_companies/
│   ├── test_rfqs/
│   └── ...
│
├── scripts/
│   ├── seed_categories.py        # Seed product/service categories + governorates
│   └── create_superadmin.py      # CLI: create admin user
│
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── .env.example
```

### Frontend (`/frontend`)

```
frontend/
├── public/
│   ├── images/
│   └── favicon.ico
├── src/
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Home page
│   │   │
│   │   ├── (public)/                  # Public route group
│   │   │   ├── search/
│   │   │   │   └── page.tsx
│   │   │   ├── companies/
│   │   │   │   ├── page.tsx           # Directory listing
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx       # Public company profile
│   │   │   ├── professionals/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx
│   │   │   ├── categories/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [slug]/
│   │   │   │       └── page.tsx
│   │   │   └── pricing/
│   │   │       └── page.tsx           # Placeholder
│   │   │
│   │   ├── (auth)/                    # Auth route group
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── signup/
│   │   │   │   └── page.tsx
│   │   │   ├── verify-email/
│   │   │   │   └── page.tsx
│   │   │   └── forgot-password/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (dashboard)/               # Authenticated route group
│   │   │   ├── layout.tsx             # Sidebar + topbar layout
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx           # Role-aware dashboard
│   │   │   ├── company/
│   │   │   │   ├── profile/
│   │   │   │   │   └── page.tsx       # Edit company profile
│   │   │   │   ├── verification/
│   │   │   │   │   └── page.tsx       # Submit/track verification
│   │   │   │   ├── team/
│   │   │   │   │   └── page.tsx       # Manage members
│   │   │   │   └── settings/
│   │   │   │       └── page.tsx
│   │   │   ├── rfqs/
│   │   │   │   ├── page.tsx           # My RFQs list
│   │   │   │   ├── create/
│   │   │   │   │   └── page.tsx       # Multi-step RFQ form
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx       # RFQ detail
│   │   │   │       └── responses/
│   │   │   │           └── page.tsx   # View responses (buyer)
│   │   │   ├── messages/
│   │   │   │   ├── page.tsx           # Thread list
│   │   │   │   └── [threadId]/
│   │   │   │       └── page.tsx       # Conversation
│   │   │   ├── shortlist/
│   │   │   │   └── page.tsx
│   │   │   ├── reviews/
│   │   │   │   └── page.tsx
│   │   │   ├── notifications/
│   │   │   │   └── page.tsx
│   │   │   └── profile/
│   │   │       └── page.tsx           # Individual profile edit
│   │   │
│   │   └── (admin)/                   # Admin route group
│   │       ├── layout.tsx             # Admin-specific layout
│   │       └── admin/
│   │           ├── page.tsx           # Admin dashboard
│   │           ├── users/
│   │           │   └── page.tsx
│   │           ├── companies/
│   │           │   └── page.tsx
│   │           ├── verification/
│   │           │   └── page.tsx       # Verification queue
│   │           ├── categories/
│   │           │   └── page.tsx
│   │           ├── reviews/
│   │           │   └── page.tsx       # Flagged reviews
│   │           ├── flags/
│   │           │   └── page.tsx
│   │           └── reports/
│   │               └── page.tsx
│   │
│   ├── components/
│   │   ├── ui/                        # Primitives: Button, Input, Select, Modal,
│   │   │                              #   Badge, Card, Table, Tabs, Tooltip, etc.
│   │   ├── layout/                    # Header, Footer, Sidebar, MobileNav
│   │   ├── forms/                     # FormField, FileUpload, MultiStep, etc.
│   │   ├── company/                   # CompanyCard, CompanyHeader, ServiceTags
│   │   ├── rfq/                       # RFQCard, RFQForm, ResponseForm, ResponseCard
│   │   ├── search/                    # SearchBar, FilterPanel, ResultCard
│   │   ├── messages/                  # ThreadList, MessageBubble, ComposeBox
│   │   ├── verification/              # VerificationBadge, DocUploader, StatusBar
│   │   └── admin/                     # StatsCard, DataTable, ActionMenu
│   │
│   ├── lib/
│   │   ├── api.ts                     # Typed API client (fetch wrapper)
│   │   ├── auth.ts                    # Token storage, auth helpers
│   │   ├── constants.ts              # App-wide constants
│   │   └── utils.ts                   # Formatting, slug, date helpers
│   │
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useCompany.ts
│   │   ├── useRfqs.ts
│   │   ├── useMessages.ts
│   │   └── useNotifications.ts
│   │
│   ├── types/
│   │   ├── api.ts                     # Generic API response types
│   │   ├── user.ts
│   │   ├── company.ts
│   │   ├── rfq.ts
│   │   ├── message.ts
│   │   └── index.ts
│   │
│   └── styles/
│       └── globals.css
│
├── Dockerfile
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.example
```

---

## STEP 3: Database Schema

### Enums

```sql
CREATE TYPE user_status AS ENUM ('active', 'suspended', 'deactivated');

CREATE TYPE account_type AS ENUM (
  'buyer', 'supplier', 'distributor', 'manufacturer',
  'contractor', 'subcontractor', 'individual', 'admin'
);

CREATE TYPE company_type AS ENUM (
  'buyer', 'supplier', 'distributor', 'manufacturer',
  'contractor', 'subcontractor'
);

CREATE TYPE company_size AS ENUM ('1-10', '11-50', '51-200', '201-500', '500+');

CREATE TYPE member_role AS ENUM ('owner', 'admin', 'manager', 'member');

CREATE TYPE verification_status AS ENUM (
  'not_submitted', 'pending', 'approved', 'rejected', 'expired', 'needs_update'
);

CREATE TYPE rfq_status AS ENUM ('draft', 'open', 'closed', 'awarded', 'cancelled');

CREATE TYPE rfq_response_status AS ENUM (
  'invited', 'viewed', 'submitted', 'revised', 'withdrawn'
);

CREATE TYPE thread_context_type AS ENUM ('direct', 'rfq', 'support');

CREATE TYPE notification_type AS ENUM (
  'email_verified', 'verification_approved', 'verification_rejected',
  'rfq_received', 'rfq_response_submitted', 'rfq_deadline_reminder',
  'new_message', 'review_received', 'account_suspended'
);

CREATE TYPE review_target_type AS ENUM ('company', 'individual');

CREATE TYPE admin_action_type AS ENUM (
  'verify_approve', 'verify_reject', 'user_suspend', 'user_activate',
  'review_remove', 'company_flag', 'category_update'
);
```

### Tables

#### Identity & Access

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    account_type    account_type NOT NULL,
    status          user_status NOT NULL DEFAULT 'active',
    email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    avatar_url      VARCHAR(500),
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE email_verification_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE password_reset_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Companies & Profiles

```sql
CREATE TABLE companies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255) NOT NULL,
    slug                VARCHAR(255) NOT NULL UNIQUE,
    company_type        company_type NOT NULL,
    description         TEXT,
    logo_url            VARCHAR(500),
    cover_url           VARCHAR(500),
    website             VARCHAR(500),
    email               VARCHAR(255),
    phone               VARCHAR(20),
    address             TEXT,
    city                VARCHAR(100),
    governorate         VARCHAR(100),
    company_size        company_size,
    year_established    INTEGER,
    commercial_reg_no   VARCHAR(100),
    tax_id              VARCHAR(100),
    verification_status verification_status NOT NULL DEFAULT 'not_submitted',
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    profile_completion  INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE company_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        member_role NOT NULL DEFAULT 'member',
    title       VARCHAR(150),
    is_primary  BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(company_id, user_id)
);

CREATE TABLE individual_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    slug                VARCHAR(255) NOT NULL UNIQUE,
    headline            VARCHAR(255),
    bio                 TEXT,
    specializations     TEXT[],
    experience_years    INTEGER,
    city                VARCHAR(100),
    governorate         VARCHAR(100),
    availability        VARCHAR(50),
    hourly_rate_egp     DECIMAL(10,2),
    resume_url          VARCHAR(500),
    verification_status verification_status NOT NULL DEFAULT 'not_submitted',
    profile_completion  INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Categories

```sql
CREATE TABLE product_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    slug        VARCHAR(150) NOT NULL UNIQUE,
    parent_id   UUID REFERENCES product_categories(id),
    description TEXT,
    icon        VARCHAR(100),
    sort_order  INTEGER NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE service_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    slug        VARCHAR(150) NOT NULL UNIQUE,
    parent_id   UUID REFERENCES service_categories(id),
    description TEXT,
    icon        VARCHAR(100),
    sort_order  INTEGER NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE governorates (
    id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name    VARCHAR(100) NOT NULL UNIQUE,
    name_ar VARCHAR(100)
);
```

#### Company Capabilities

```sql
CREATE TABLE company_services (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    service_category_id UUID NOT NULL REFERENCES service_categories(id),
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(company_id, service_category_id)
);

CREATE TABLE company_products (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    product_category_id UUID NOT NULL REFERENCES product_categories(id),
    brand_names         TEXT[],
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(company_id, product_category_id)
);

CREATE TABLE certifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_id      UUID REFERENCES individual_profiles(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    issuing_body    VARCHAR(255),
    issue_date      DATE,
    expiry_date     DATE,
    document_url    VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (company_id IS NOT NULL OR profile_id IS NOT NULL)
);

CREATE TABLE project_references (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_id      UUID REFERENCES individual_profiles(id) ON DELETE CASCADE,
    project_name    VARCHAR(255) NOT NULL,
    client_name     VARCHAR(255),
    description     TEXT,
    location        VARCHAR(255),
    year            INTEGER,
    scope           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (company_id IS NOT NULL OR profile_id IS NOT NULL)
);

CREATE TABLE profile_media (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_id  UUID REFERENCES individual_profiles(id) ON DELETE CASCADE,
    media_type  VARCHAR(50) NOT NULL,
    url         VARCHAR(500) NOT NULL,
    title       VARCHAR(255),
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (company_id IS NOT NULL OR profile_id IS NOT NULL)
);
```

#### Verification

```sql
CREATE TABLE verification_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_id      UUID REFERENCES individual_profiles(id) ON DELETE CASCADE,
    status          verification_status NOT NULL DEFAULT 'pending',
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at     TIMESTAMPTZ,
    reviewed_by     UUID REFERENCES users(id),
    admin_notes     TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (company_id IS NOT NULL OR profile_id IS NOT NULL)
);

CREATE TABLE verification_documents (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_request_id UUID NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
    document_type           VARCHAR(100) NOT NULL,
    file_url                VARCHAR(500) NOT NULL,
    file_name               VARCHAR(255) NOT NULL,
    uploaded_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### RFQ

```sql
CREATE TABLE rfqs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(id),
    created_by      UUID NOT NULL REFERENCES users(id),
    title           VARCHAR(255) NOT NULL,
    request_type    VARCHAR(100) NOT NULL,
    category_id     UUID,
    category_type   VARCHAR(20),
    description     TEXT NOT NULL,
    location        VARCHAR(255),
    governorate     VARCHAR(100),
    quantity_scope  TEXT,
    timeline        VARCHAR(255),
    deadline        TIMESTAMPTZ NOT NULL,
    notes           TEXT,
    status          rfq_status NOT NULL DEFAULT 'draft',
    awarded_to      UUID REFERENCES companies(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rfq_attachments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id      UUID NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
    file_url    VARCHAR(500) NOT NULL,
    file_name   VARCHAR(255) NOT NULL,
    file_size   INTEGER,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rfq_invitations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id          UUID NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
    company_id      UUID NOT NULL REFERENCES companies(id),
    status          rfq_response_status NOT NULL DEFAULT 'invited',
    invited_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    viewed_at       TIMESTAMPTZ,
    UNIQUE(rfq_id, company_id)
);

CREATE TABLE rfq_responses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id          UUID NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
    company_id      UUID NOT NULL REFERENCES companies(id),
    submitted_by    UUID NOT NULL REFERENCES users(id),
    cover_note      TEXT,
    quoted_amount   DECIMAL(15,2),
    currency        VARCHAR(10) DEFAULT 'EGP',
    delivery_time   VARCHAR(255),
    notes           TEXT,
    file_url        VARCHAR(500),
    file_name       VARCHAR(255),
    status          rfq_response_status NOT NULL DEFAULT 'submitted',
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(rfq_id, company_id)
);

CREATE TABLE rfq_status_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id      UUID NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
    old_status  rfq_status,
    new_status  rfq_status NOT NULL,
    changed_by  UUID REFERENCES users(id),
    note        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Messaging

```sql
CREATE TABLE message_threads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type    thread_context_type NOT NULL,
    context_id      UUID,
    subject         VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE message_participants (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id    UUID NOT NULL REFERENCES message_threads(id) ON DELETE CASCADE,
    user_id      UUID NOT NULL REFERENCES users(id),
    company_id   UUID REFERENCES companies(id),
    joined_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_read_at TIMESTAMPTZ,
    UNIQUE(thread_id, user_id)
);

CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id   UUID NOT NULL REFERENCES message_threads(id) ON DELETE CASCADE,
    sender_id   UUID NOT NULL REFERENCES users(id),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE message_attachments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id  UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    file_url    VARCHAR(500) NOT NULL,
    file_name   VARCHAR(255) NOT NULL,
    file_size   INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Reviews

```sql
CREATE TABLE reviews (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reviewer_id         UUID NOT NULL REFERENCES users(id),
    reviewer_company_id UUID REFERENCES companies(id),
    target_type         review_target_type NOT NULL,
    target_company_id   UUID REFERENCES companies(id),
    target_profile_id   UUID REFERENCES individual_profiles(id),
    rfq_id              UUID REFERENCES rfqs(id),
    overall_rating      SMALLINT NOT NULL CHECK (overall_rating BETWEEN 1 AND 5),
    response_speed      SMALLINT CHECK (response_speed BETWEEN 1 AND 5),
    communication       SMALLINT CHECK (communication BETWEEN 1 AND 5),
    documentation       SMALLINT CHECK (documentation BETWEEN 1 AND 5),
    comment             TEXT,
    is_visible          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE review_flags (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id   UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    flagged_by  UUID NOT NULL REFERENCES users(id),
    reason      TEXT NOT NULL,
    resolved    BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Notifications

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            notification_type NOT NULL,
    title           VARCHAR(255) NOT NULL,
    body            TEXT,
    link            VARCHAR(500),
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### Admin & Shortlists

```sql
CREATE TABLE admin_action_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id    UUID NOT NULL REFERENCES users(id),
    action_type admin_action_type NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id   UUID NOT NULL,
    details     JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE shortlists (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id  UUID REFERENCES companies(id) ON DELETE CASCADE,
    profile_id  UUID REFERENCES individual_profiles(id) ON DELETE CASCADE,
    note        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (company_id IS NOT NULL OR profile_id IS NOT NULL)
);
```

#### Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_account_type ON users(account_type);
CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_type ON companies(company_type);
CREATE INDEX idx_companies_verification ON companies(verification_status);
CREATE INDEX idx_companies_governorate ON companies(governorate);
CREATE INDEX idx_company_members_user ON company_members(user_id);
CREATE INDEX idx_company_members_company ON company_members(company_id);
CREATE INDEX idx_individual_profiles_slug ON individual_profiles(slug);
CREATE INDEX idx_rfqs_company ON rfqs(company_id);
CREATE INDEX idx_rfqs_status ON rfqs(status);
CREATE INDEX idx_rfq_invitations_company ON rfq_invitations(company_id);
CREATE INDEX idx_rfq_responses_rfq ON rfq_responses(rfq_id);
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_reviews_target_company ON reviews(target_company_id);
CREATE INDEX idx_shortlists_user ON shortlists(user_id);

-- Full-text search
CREATE INDEX idx_companies_search ON companies USING gin(
    to_tsvector('english', coalesce(name,'') || ' ' || coalesce(description,''))
);
```

### Entity Relationship Summary

```
users ──< company_members >── companies
users ──── individual_profiles
companies ──< company_services >── service_categories
companies ──< company_products >── product_categories
companies ──< certifications
companies ──< project_references
companies ──< profile_media
companies ──< verification_requests ──< verification_documents
companies ──< rfq_invitations >── rfqs
rfqs ──< rfq_attachments
rfqs ──< rfq_responses
rfqs ──< rfq_status_history
message_threads ──< messages ──< message_attachments
message_threads ──< message_participants
reviews ──< review_flags
users ──< notifications
users ──< shortlists
users ──< admin_action_logs
```

---

## STEP 4: Role-Permission Matrix

| Permission                    | Public | Auth User | Buyer Admin | Buyer Member | Supplier/Contractor Admin | Sales User | Individual Pro | Platform Admin |
|-------------------------------|--------|-----------|-------------|--------------|---------------------------|------------|----------------|----------------|
| View public profiles          | yes    | yes       | yes         | yes          | yes                       | yes        | yes            | yes            |
| Search companies/profiles     | yes    | yes       | yes         | yes          | yes                       | yes        | yes            | yes            |
| Sign up / login               | yes    | -         | -           | -            | -                         | -          | -              | -              |
| Edit own user profile         | -      | yes       | yes         | yes          | yes                       | yes        | yes            | yes            |
| Create company                | -      | yes       | -           | -            | -                         | -          | -              | -              |
| Edit company profile          | -      | -         | yes         | -            | yes                       | -          | -              | yes            |
| Manage company team           | -      | -         | yes         | -            | yes                       | -          | -              | yes            |
| Submit verification           | -      | -         | yes         | -            | yes                       | -          | yes            | yes            |
| Create RFQ                    | -      | -         | yes         | yes          | -                         | -          | -              | -              |
| Invite vendors to RFQ         | -      | -         | yes         | yes          | -                         | -          | -              | -              |
| View own company RFQs         | -      | -         | yes         | yes          | yes                       | yes        | -              | -              |
| Respond to RFQ                | -      | -         | -           | -            | yes                       | yes        | -              | -              |
| View RFQ responses (buyer)    | -      | -         | yes         | yes          | -                         | -          | -              | -              |
| Send messages                 | -      | -         | yes         | yes          | yes                       | yes        | yes            | -              |
| Shortlist companies           | -      | -         | yes         | yes          | -                         | -          | -              | -              |
| Write reviews                 | -      | -         | yes         | yes          | yes                       | yes        | yes            | -              |
| Edit individual profile       | -      | -         | -           | -            | -                         | -          | yes            | -              |
| Verify/reject submissions     | -      | -         | -           | -            | -                         | -          | -              | yes            |
| Suspend/activate users        | -      | -         | -           | -            | -                         | -          | -              | yes            |
| Manage categories             | -      | -         | -           | -            | -                         | -          | -              | yes            |
| Moderate reviews              | -      | -         | -           | -            | -                         | -          | -              | yes            |
| View admin reports            | -      | -         | -           | -            | -                         | -          | -              | yes            |
| View admin action logs        | -      | -         | -           | -            | -                         | -          | -              | yes            |

### Notes

- **Buyer Member** can create RFQs but cannot manage company settings or team
- **Sales User** can draft RFQ responses but cannot edit the company profile
- **Individual Professional** has their own profile, not tied to a company
- **Admin** moderates — does not create RFQs or respond to them

---

## STEP 5: MVP API Endpoints

### Auth — `/api/v1/auth`

| Method | Path               | Description                           |
|--------|--------------------|---------------------------------------|
| POST   | `/register`        | Sign up                               |
| POST   | `/login`           | Login → access + refresh tokens       |
| POST   | `/refresh`         | Refresh access token                  |
| POST   | `/logout`          | Revoke refresh token                  |
| POST   | `/verify-email`    | Verify email with token               |
| POST   | `/forgot-password` | Request password reset email          |
| POST   | `/reset-password`  | Reset password with token             |
| GET    | `/me`              | Get current authenticated user        |

### Users — `/api/v1/users`

| Method | Path          | Description            |
|--------|---------------|------------------------|
| GET    | `/{id}`       | Get user public info   |
| PATCH  | `/me`         | Update current user    |
| PATCH  | `/me/avatar`  | Upload avatar          |

### Companies — `/api/v1/companies`

| Method | Path                              | Description              |
|--------|-----------------------------------|--------------------------|
| POST   | `/`                               | Create company           |
| GET    | `/`                               | List (public, filtered)  |
| GET    | `/{slug}`                         | Get public profile       |
| PATCH  | `/{id}`                           | Update (owner/admin)     |
| POST   | `/{id}/logo`                      | Upload logo              |
| GET    | `/{id}/members`                   | List team members        |
| POST   | `/{id}/members`                   | Invite member            |
| PATCH  | `/{id}/members/{memberId}`        | Update member role       |
| DELETE | `/{id}/members/{memberId}`        | Remove member            |
| POST   | `/{id}/services`                  | Add service category     |
| DELETE | `/{id}/services/{serviceId}`      | Remove service           |
| POST   | `/{id}/products`                  | Add product category     |
| DELETE | `/{id}/products/{productId}`      | Remove product           |
| POST   | `/{id}/certifications`            | Add certification        |
| DELETE | `/{id}/certifications/{certId}`   | Remove certification     |
| POST   | `/{id}/references`                | Add project reference    |
| DELETE | `/{id}/references/{refId}`        | Remove reference         |
| POST   | `/{id}/media`                     | Upload media             |
| DELETE | `/{id}/media/{mediaId}`           | Remove media             |

### Individual Profiles — `/api/v1/profiles`

| Method | Path                       | Description           |
|--------|----------------------------|-----------------------|
| POST   | `/`                        | Create profile        |
| GET    | `/`                        | List (public)         |
| GET    | `/{slug}`                  | Get public profile    |
| PATCH  | `/{id}`                    | Update own profile    |
| POST   | `/{id}/certifications`     | Add certification     |
| POST   | `/{id}/references`         | Add reference         |

### Categories — `/api/v1/categories`

| Method | Path              | Description                   |
|--------|-------------------|-------------------------------|
| GET    | `/products`       | List product categories       |
| GET    | `/services`       | List service categories       |
| GET    | `/governorates`   | List governorates             |
| POST   | `/products`       | Create product category (admin)|
| POST   | `/services`       | Create service category (admin)|
| PATCH  | `/products/{id}`  | Update (admin)                |
| PATCH  | `/services/{id}`  | Update (admin)                |

### Search — `/api/v1/search`

| Method | Path          | Description                                  |
|--------|---------------|----------------------------------------------|
| GET    | `/`           | Unified search (companies + profiles)        |
| GET    | `/companies`  | Search companies (type, category, gov, keyword) |
| GET    | `/profiles`   | Search individual profiles                   |

### Verification — `/api/v1/verification`

| Method | Path             | Description                    |
|--------|------------------|--------------------------------|
| POST   | `/submit`        | Submit verification request    |
| GET    | `/status`        | Get own verification status    |
| GET    | `/queue`         | Admin: list pending requests   |
| GET    | `/{id}`          | Admin: get request detail      |
| POST   | `/{id}/approve`  | Admin: approve                 |
| POST   | `/{id}/reject`   | Admin: reject with notes       |

### RFQs — `/api/v1/rfqs`

| Method | Path                       | Description                      |
|--------|----------------------------|----------------------------------|
| POST   | `/`                        | Create RFQ                       |
| GET    | `/`                        | List own/received RFQs           |
| GET    | `/{id}`                    | Get RFQ detail                   |
| PATCH  | `/{id}`                    | Update RFQ (draft only)          |
| POST   | `/{id}/publish`            | Publish draft → open             |
| POST   | `/{id}/close`              | Close RFQ                        |
| POST   | `/{id}/cancel`             | Cancel RFQ                       |
| POST   | `/{id}/award`              | Award RFQ to a company           |
| POST   | `/{id}/attachments`        | Upload attachment                |
| POST   | `/{id}/invite`             | Invite companies                 |
| GET    | `/{id}/invitations`        | List invitations                 |
| GET    | `/{id}/responses`          | List responses (buyer)           |
| POST   | `/{id}/responses`          | Submit response (supplier)       |
| PATCH  | `/{id}/responses/{respId}` | Update response before deadline  |

### Messages — `/api/v1/messages`

| Method | Path                                       | Description          |
|--------|---------------------------------------------|----------------------|
| GET    | `/threads`                                  | List threads         |
| POST   | `/threads`                                  | Create new thread    |
| GET    | `/threads/{id}`                             | Get thread + messages|
| POST   | `/threads/{id}/messages`                    | Send message         |
| POST   | `/threads/{id}/read`                        | Mark as read         |
| POST   | `/threads/{id}/messages/{msgId}/attachments` | Upload attachment   |

### Reviews — `/api/v1/reviews`

| Method | Path                      | Description              |
|--------|---------------------------|--------------------------|
| POST   | `/`                       | Create review            |
| GET    | `/company/{companyId}`    | List reviews for company |
| GET    | `/profile/{profileId}`   | List reviews for profile |
| POST   | `/{id}/flag`             | Flag a review            |

### Notifications — `/api/v1/notifications`

| Method | Path            | Description       |
|--------|-----------------|--------------------|
| GET    | `/`             | List notifications |
| GET    | `/unread-count` | Unread count       |
| POST   | `/{id}/read`    | Mark as read       |
| POST   | `/read-all`     | Mark all as read   |

### Shortlists — `/api/v1/shortlists`

| Method | Path     | Description           |
|--------|----------|-----------------------|
| GET    | `/`      | List shortlisted items|
| POST   | `/`      | Add to shortlist      |
| DELETE | `/{id}`  | Remove from shortlist |

### Admin — `/api/v1/admin`

| Method | Path                          | Description            |
|--------|-------------------------------|------------------------|
| GET    | `/dashboard`                  | Dashboard stats        |
| GET    | `/users`                      | List all users         |
| PATCH  | `/users/{id}/status`          | Suspend/activate       |
| GET    | `/companies`                  | List all companies     |
| GET    | `/reviews`                    | List flagged reviews   |
| POST   | `/reviews/{id}/hide`          | Hide review            |
| POST   | `/reviews/{id}/dismiss-flag`  | Dismiss flag           |
| GET    | `/logs`                       | Admin action logs      |
| GET    | `/reports`                    | Platform reports       |

---

## STEP 6: Sprint Backlog

### Sprint 1 — Foundation (Week 1–2)

| #  | Task                                                        | Type     |
|----|-------------------------------------------------------------|----------|
| 1  | Project scaffolding: backend (FastAPI), pyproject.toml, requirements | Backend  |
| 2  | Project scaffolding: frontend (Next.js + TS + Tailwind)     | Frontend |
| 3  | docker-compose.yml (Postgres, Redis, MinIO, backend, frontend) | DevOps   |
| 4  | Dockerfiles for backend and frontend                        | DevOps   |
| 5  | .env.example files for both services                        | DevOps   |
| 6  | FastAPI app factory, config, database session setup          | Backend  |
| 7  | Alembic init + first migration (users, tokens tables)        | Backend  |
| 8  | SQLAlchemy models: User, EmailVerificationToken, PasswordResetToken, RefreshToken | Backend  |
| 9  | Auth module: register, login, JWT, refresh, logout           | Backend  |
| 10 | Auth module: email verification, forgot/reset password       | Backend  |
| 11 | Auth dependencies: get_current_user, require_role            | Backend  |
| 12 | Password hashing (bcrypt), JWT utils                         | Backend  |
| 13 | CORS middleware, request validation error handlers           | Backend  |
| 14 | Base UI components: Button, Input, Card, Badge, Modal        | Frontend |
| 15 | Layout components: Header, Footer, MobileNav                 | Frontend |
| 16 | Home page (public)                                           | Frontend |
| 17 | Login page + form                                            | Frontend |
| 18 | Signup page + form (account type selection)                  | Frontend |
| 19 | API client lib (typed fetch wrapper)                         | Frontend |
| 20 | Auth hooks + token storage                                   | Frontend |

### Sprint 2 — Profiles & Categories (Week 3–4)

| #  | Task                                                        | Type     |
|----|-------------------------------------------------------------|----------|
| 21 | Migration: companies, company_members, individual_profiles   | Backend  |
| 22 | Migration: categories, governorates, company_services/products | Backend  |
| 23 | Migration: certifications, project_references, profile_media | Backend  |
| 24 | SQLAlchemy models for all Sprint 2 tables                    | Backend  |
| 25 | Company CRUD endpoints                                       | Backend  |
| 26 | Company members management endpoints                         | Backend  |
| 27 | Company services/products/certifications/references endpoints | Backend  |
| 28 | Individual profile CRUD endpoints                            | Backend  |
| 29 | Category CRUD endpoints (admin)                              | Backend  |
| 30 | Governorates endpoint                                        | Backend  |
| 31 | S3/MinIO storage service: upload, download, presigned URLs   | Backend  |
| 32 | File upload endpoints (logo, media, documents)               | Backend  |
| 33 | Seed script: categories + governorates                       | Backend  |
| 34 | Profile completion calculation logic                         | Backend  |
| 35 | Slug generation with collision handling                      | Backend  |
| 36 | Onboarding flow UI (post-signup wizard)                      | Frontend |
| 37 | Company profile editor (multi-section form)                  | Frontend |
| 38 | Public company profile page                                  | Frontend |
| 39 | Individual profile editor                                    | Frontend |
| 40 | Public individual profile page                               | Frontend |
| 41 | Category listing pages                                       | Frontend |
| 42 | Profile completion progress indicator                        | Frontend |
| 43 | File upload component (drag-and-drop)                        | Frontend |
| 44 | Dashboard layout (sidebar + topbar)                          | Frontend |

### Sprint 3 — Search & Verification (Week 5–6)

| #  | Task                                                        | Type     |
|----|-------------------------------------------------------------|----------|
| 45 | Migration: verification_requests, verification_documents     | Backend  |
| 46 | SQLAlchemy models for verification                           | Backend  |
| 47 | Search API: companies (keyword, type, category, gov, verified) | Backend  |
| 48 | Search API: individual profiles                              | Backend  |
| 49 | Unified search endpoint                                      | Backend  |
| 50 | PostgreSQL full-text search integration                      | Backend  |
| 51 | Verification submit endpoint                                 | Backend  |
| 52 | Verification status endpoint                                 | Backend  |
| 53 | Admin: verification queue endpoint                           | Backend  |
| 54 | Admin: approve/reject/request-correction endpoints           | Backend  |
| 55 | Admin action logging for verification                        | Backend  |
| 56 | create_superadmin.py script                                  | Backend  |
| 57 | Search page UI with filters                                  | Frontend |
| 58 | Search result cards (company + individual)                   | Frontend |
| 59 | Filter panel (type, category, governorate, verified)         | Frontend |
| 60 | Verification submission page (document upload)               | Frontend |
| 61 | Verification status tracker                                  | Frontend |
| 62 | Verification badge component                                 | Frontend |
| 63 | Admin layout + admin dashboard (basic stats)                 | Frontend |
| 64 | Admin: verification queue page                               | Frontend |
| 65 | Admin: verification detail + approve/reject UI               | Frontend |

### Sprint 4 — RFQ Workflow (Week 7–8)

| #  | Task                                                        | Type     |
|----|-------------------------------------------------------------|----------|
| 66 | Migration: rfqs, rfq_attachments, rfq_invitations, rfq_responses, rfq_status_history | Backend  |
| 67 | SQLAlchemy models for RFQ                                    | Backend  |
| 68 | RFQ create/update/list/detail endpoints                      | Backend  |
| 69 | RFQ publish/close/cancel/award endpoints                     | Backend  |
| 70 | RFQ attachment upload endpoint                               | Backend  |
| 71 | RFQ invitation endpoint (invite companies)                   | Backend  |
| 72 | RFQ response submit/update endpoints                         | Backend  |
| 73 | RFQ responses list for buyer                                 | Backend  |
| 74 | RFQ status history tracking                                  | Backend  |
| 75 | Access control: only invited companies see RFQ               | Backend  |
| 76 | Shortlist CRUD endpoints                                     | Backend  |
| 77 | RFQ creation form (multi-step)                               | Frontend |
| 78 | RFQ list page (buyer: my RFQs, supplier: incoming)           | Frontend |
| 79 | RFQ detail page                                              | Frontend |
| 80 | Vendor invitation flow (search + select + invite)            | Frontend |
| 81 | RFQ response form (supplier)                                 | Frontend |
| 82 | RFQ responses comparison view (buyer)                        | Frontend |
| 83 | RFQ status management UI                                     | Frontend |
| 84 | Shortlist page                                               | Frontend |

### Sprint 5 — Messaging & Notifications (Week 9–10)

| #  | Task                                                        | Type     |
|----|-------------------------------------------------------------|----------|
| 85 | Migration: message_threads, message_participants, messages, message_attachments | Backend  |
| 86 | Migration: notifications                                     | Backend  |
| 87 | SQLAlchemy models for messages + notifications               | Backend  |
| 88 | Message thread create/list/detail endpoints                  | Backend  |
| 89 | Send message endpoint                                        | Backend  |
| 90 | Mark thread as read endpoint                                 | Backend  |
| 91 | Message attachment upload                                    | Backend  |
| 92 | Auto-create RFQ thread on invite/response                    | Backend  |
| 93 | Notification CRUD endpoints                                  | Backend  |
| 94 | Notification creation service (triggered by events)          | Backend  |
| 95 | Background worker: email notification dispatch               | Backend  |
| 96 | Email templates (verification, RFQ, message, etc.)           | Backend  |
| 97 | Thread list UI                                               | Frontend |
| 98 | Conversation view (message bubbles + compose)                | Frontend |
| 99 | Message attachment support in UI                             | Frontend |
| 100| Polling for new messages (10-15s on active thread)           | Frontend |
| 101| Notification bell + dropdown                                 | Frontend |
| 102| Notifications page                                           | Frontend |
| 103| Unread badge on sidebar items                                | Frontend |

### Sprint 6 — Reviews, Admin, Hardening (Week 11–12)

| #  | Task                                                        | Type     |
|----|-------------------------------------------------------------|----------|
| 104| Migration: reviews, review_flags, admin_action_logs, shortlists | Backend  |
| 105| SQLAlchemy models for reviews + admin logs                   | Backend  |
| 106| Review create/list endpoints                                 | Backend  |
| 107| Review flag endpoint                                         | Backend  |
| 108| Admin: flagged reviews list + moderate endpoints             | Backend  |
| 109| Admin: user management endpoints (list, suspend, activate)   | Backend  |
| 110| Admin: company management endpoints                          | Backend  |
| 111| Admin: category CRUD endpoints                               | Backend  |
| 112| Admin: reports endpoint (counts, stats)                      | Backend  |
| 113| Admin: action log endpoints                                  | Backend  |
| 114| Rate limiting middleware                                     | Backend  |
| 115| File type/size validation on all uploads                     | Backend  |
| 116| Secure file access (presigned URLs, not public)              | Backend  |
| 117| Review display on company/profile pages                      | Frontend |
| 118| Review creation form                                         | Frontend |
| 119| Admin: user management page                                  | Frontend |
| 120| Admin: company management page                               | Frontend |
| 121| Admin: category management page                              | Frontend |
| 122| Admin: flagged reviews page                                  | Frontend |
| 123| Admin: reports page                                          | Frontend |
| 124| Responsive design QA pass                                    | Frontend |
| 125| Error states and loading skeletons                           | Frontend |
| 126| README: local setup guide                                    | Docs     |
| 127| README: deployment guide                                     | Docs     |
| 128| Final security audit pass                                    | Backend  |

---

## Assumptions

1. **Single currency (EGP)** for MVP — multi-currency deferred
2. **Email-only auth** — no social login in MVP
3. **One company ownership per user** — but a user can be member of multiple companies
4. **Polling for messages** (10-15s) — no WebSockets in MVP
5. **Categories are admin-managed** — seeded with fiber-specific data
6. **File uploads**: PDF, DOC/DOCX, XLS/XLSX, JPG, PNG; max 10MB per file
7. **Verification is per-entity** (company or individual) — one request bundles all docs
8. **RFQs are invitation-only** — not publicly browsable
9. **Reviews require auth** but not strictly a completed transaction in MVP — admin moderates
10. **English-first UI** — Arabic deferred, but `name_ar` fields are ready in DB
11. **No payment/subscription** — all features free in MVP; pricing page is placeholder
12. **MinIO locally, S3 in production** — same API via env var switch
13. **Background jobs via arq** (lightweight Redis-based) — not Celery
14. **Admin created via CLI script** — not self-registration
15. **Slugs auto-generated** from names with collision handling (append `-2`, `-3`, etc.)
