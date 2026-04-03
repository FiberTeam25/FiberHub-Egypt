"""Initial schema - all tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-04-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Enum types
    # ------------------------------------------------------------------
    account_type = sa.Enum(
        "buyer", "supplier", "distributor", "manufacturer",
        "contractor", "subcontractor", "individual", "admin",
        name="account_type", create_type=False,
    )
    user_status = sa.Enum("active", "suspended", "deactivated", name="user_status", create_type=False)
    company_type = sa.Enum(
        "buyer", "supplier", "distributor", "manufacturer",
        "contractor", "subcontractor",
        name="company_type", create_type=False,
    )
    company_size = sa.Enum("1-10", "11-50", "51-200", "201-500", "500+", name="company_size", create_type=False)
    member_role = sa.Enum("owner", "admin", "manager", "member", name="member_role", create_type=False)
    verification_status = sa.Enum(
        "not_submitted", "pending", "approved", "rejected", "expired", "needs_update",
        name="verification_status", create_type=False,
    )
    rfq_status = sa.Enum("draft", "open", "closed", "awarded", "cancelled", name="rfq_status", create_type=False)
    rfq_response_status = sa.Enum(
        "invited", "viewed", "submitted", "revised", "withdrawn",
        name="rfq_response_status", create_type=False,
    )
    thread_context_type = sa.Enum("direct", "rfq", "support", name="thread_context_type", create_type=False)
    review_target_type = sa.Enum("company", "individual", name="review_target_type", create_type=False)
    notification_type = sa.Enum(
        "email_verified", "verification_approved", "verification_rejected",
        "rfq_received", "rfq_response_submitted", "rfq_deadline_reminder",
        "new_message", "review_received", "account_suspended",
        name="notification_type", create_type=False,
    )
    admin_action_type = sa.Enum(
        "verify_approve", "verify_reject", "user_suspend", "user_activate",
        "review_remove", "company_flag", "category_update",
        name="admin_action_type", create_type=False,
    )

    # Create enum types explicitly (IF NOT EXISTS via checkfirst)
    for enum in [account_type, user_status, company_type, company_size, member_role,
                 verification_status, rfq_status, rfq_response_status, thread_context_type,
                 review_target_type, notification_type, admin_action_type]:
        enum.create(op.get_bind(), checkfirst=True)

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("account_type", account_type, nullable=False),
        sa.Column("status", user_status, nullable=False, server_default="active"),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # email_verification_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("token", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # password_reset_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("token", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # refresh_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("token_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # governorates
    # ------------------------------------------------------------------
    op.create_table(
        "governorates",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("name_ar", sa.String(100), nullable=True),
    )

    # ------------------------------------------------------------------
    # product_categories
    # ------------------------------------------------------------------
    op.create_table(
        "product_categories",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("slug", sa.String(150), unique=True, nullable=False),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("product_categories.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # service_categories
    # ------------------------------------------------------------------
    op.create_table(
        "service_categories",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("slug", sa.String(150), unique=True, nullable=False),
        sa.Column("parent_id", sa.String(36), sa.ForeignKey("service_categories.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # companies
    # ------------------------------------------------------------------
    op.create_table(
        "companies",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("company_type", company_type, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("cover_url", sa.String(500), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("governorate", sa.String(100), nullable=True),
        sa.Column("company_size", company_size, nullable=True),
        sa.Column("year_established", sa.Integer(), nullable=True),
        sa.Column("commercial_reg_no", sa.String(100), nullable=True),
        sa.Column("tax_id", sa.String(100), nullable=True),
        sa.Column("verification_status", verification_status, nullable=False, server_default="not_submitted"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("profile_completion", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_companies_type", "companies", ["company_type"])
    op.create_index("idx_companies_verification", "companies", ["verification_status"])
    op.create_index("idx_companies_governorate", "companies", ["governorate"])

    # ------------------------------------------------------------------
    # individual_profiles
    # ------------------------------------------------------------------
    op.create_table(
        "individual_profiles",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("headline", sa.String(255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("specializations", ARRAY(sa.String()), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("governorate", sa.String(100), nullable=True),
        sa.Column("availability", sa.String(50), nullable=True),
        sa.Column("hourly_rate_egp", sa.Numeric(10, 2), nullable=True),
        sa.Column("resume_url", sa.String(500), nullable=True),
        sa.Column("verification_status", verification_status, nullable=False, server_default="not_submitted"),
        sa.Column("profile_completion", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # company_members
    # ------------------------------------------------------------------
    op.create_table(
        "company_members",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", member_role, nullable=False, server_default="member"),
        sa.Column("title", sa.String(150), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("company_id", "user_id", name="uq_company_member"),
    )
    op.create_index("idx_company_members_user", "company_members", ["user_id"])
    op.create_index("idx_company_members_company", "company_members", ["company_id"])

    # ------------------------------------------------------------------
    # company_services
    # ------------------------------------------------------------------
    op.create_table(
        "company_services",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_category_id", sa.String(36), sa.ForeignKey("service_categories.id"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("company_id", "service_category_id", name="uq_company_service"),
    )

    # ------------------------------------------------------------------
    # company_products
    # ------------------------------------------------------------------
    op.create_table(
        "company_products",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_category_id", sa.String(36), sa.ForeignKey("product_categories.id"), nullable=False),
        sa.Column("brand_names", ARRAY(sa.String()), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("company_id", "product_category_id", name="uq_company_product"),
    )

    # ------------------------------------------------------------------
    # certifications
    # ------------------------------------------------------------------
    op.create_table(
        "certifications",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("individual_profiles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("issuing_body", sa.String(255), nullable=True),
        sa.Column("issue_date", sa.String(20), nullable=True),
        sa.Column("expiry_date", sa.String(20), nullable=True),
        sa.Column("document_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("company_id IS NOT NULL OR profile_id IS NOT NULL", name="ck_cert_owner"),
    )

    # ------------------------------------------------------------------
    # project_references
    # ------------------------------------------------------------------
    op.create_table(
        "project_references",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("individual_profiles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("project_name", sa.String(255), nullable=False),
        sa.Column("client_name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("company_id IS NOT NULL OR profile_id IS NOT NULL", name="ck_ref_owner"),
    )

    # ------------------------------------------------------------------
    # profile_media
    # ------------------------------------------------------------------
    op.create_table(
        "profile_media",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("individual_profiles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("media_type", sa.String(50), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("company_id IS NOT NULL OR profile_id IS NOT NULL", name="ck_media_owner"),
    )

    # ------------------------------------------------------------------
    # verification_requests
    # ------------------------------------------------------------------
    op.create_table(
        "verification_requests",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("individual_profiles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("status", verification_status, nullable=False, server_default="pending"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("company_id IS NOT NULL OR profile_id IS NOT NULL", name="ck_verif_owner"),
    )

    # ------------------------------------------------------------------
    # verification_documents
    # ------------------------------------------------------------------
    op.create_table(
        "verification_documents",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("verification_request_id", sa.String(36), sa.ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # rfqs
    # ------------------------------------------------------------------
    op.create_table(
        "rfqs",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("request_type", sa.String(100), nullable=False),
        sa.Column("category_id", sa.String(36), nullable=True),
        sa.Column("category_type", sa.String(20), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("governorate", sa.String(100), nullable=True),
        sa.Column("quantity_scope", sa.Text(), nullable=True),
        sa.Column("timeline", sa.String(255), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", rfq_status, nullable=False, server_default="draft"),
        sa.Column("awarded_to", sa.String(36), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_rfqs_company", "rfqs", ["company_id"])
    op.create_index("idx_rfqs_status", "rfqs", ["status"])

    # ------------------------------------------------------------------
    # rfq_attachments
    # ------------------------------------------------------------------
    op.create_table(
        "rfq_attachments",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # rfq_invitations
    # ------------------------------------------------------------------
    op.create_table(
        "rfq_invitations",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("status", rfq_response_status, nullable=False, server_default="invited"),
        sa.Column("invited_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("rfq_id", "company_id", name="uq_rfq_invitation"),
    )
    op.create_index("idx_rfq_invitations_company", "rfq_invitations", ["company_id"])

    # ------------------------------------------------------------------
    # rfq_responses
    # ------------------------------------------------------------------
    op.create_table(
        "rfq_responses",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("submitted_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("cover_note", sa.Text(), nullable=True),
        sa.Column("quoted_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("currency", sa.String(10), nullable=True, server_default="EGP"),
        sa.Column("delivery_time", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=True),
        sa.Column("status", rfq_response_status, nullable=False, server_default="submitted"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("rfq_id", "company_id", name="uq_rfq_response"),
    )
    op.create_index("idx_rfq_responses_rfq", "rfq_responses", ["rfq_id"])

    # ------------------------------------------------------------------
    # rfq_status_history
    # ------------------------------------------------------------------
    op.create_table(
        "rfq_status_history",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("old_status", rfq_status, nullable=True),
        sa.Column("new_status", rfq_status, nullable=False),
        sa.Column("changed_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # message_threads
    # ------------------------------------------------------------------
    op.create_table(
        "message_threads",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("context_type", thread_context_type, nullable=False),
        sa.Column("context_id", sa.String(36), nullable=True),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # message_participants
    # ------------------------------------------------------------------
    op.create_table(
        "message_participants",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("thread_id", sa.String(36), sa.ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("thread_id", "user_id", name="uq_thread_participant"),
    )

    # ------------------------------------------------------------------
    # messages
    # ------------------------------------------------------------------
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("thread_id", sa.String(36), sa.ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_messages_thread", "messages", ["thread_id"])

    # ------------------------------------------------------------------
    # message_attachments
    # ------------------------------------------------------------------
    op.create_table(
        "message_attachments",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("message_id", sa.String(36), sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # reviews
    # ------------------------------------------------------------------
    op.create_table(
        "reviews",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewer_company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("target_type", review_target_type, nullable=False),
        sa.Column("target_company_id", sa.String(36), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("target_profile_id", sa.String(36), sa.ForeignKey("individual_profiles.id"), nullable=True),
        sa.Column("rfq_id", sa.String(36), sa.ForeignKey("rfqs.id"), nullable=True),
        sa.Column("overall_rating", sa.SmallInteger(), nullable=False),
        sa.Column("response_speed", sa.SmallInteger(), nullable=True),
        sa.Column("communication", sa.SmallInteger(), nullable=True),
        sa.Column("documentation", sa.SmallInteger(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("overall_rating BETWEEN 1 AND 5", name="ck_overall_rating"),
    )
    op.create_index("idx_reviews_target_company", "reviews", ["target_company_id"])

    # ------------------------------------------------------------------
    # review_flags
    # ------------------------------------------------------------------
    op.create_table(
        "review_flags",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("review_id", sa.String(36), sa.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("flagged_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("resolved_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("email_sent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_notifications_user", "notifications", ["user_id", "is_read"])

    # ------------------------------------------------------------------
    # admin_action_logs
    # ------------------------------------------------------------------
    op.create_table(
        "admin_action_logs",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("admin_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action_type", admin_action_type, nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(36), nullable=False),
        sa.Column("details", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # shortlists
    # ------------------------------------------------------------------
    op.create_table(
        "shortlists",
        sa.Column("id", sa.String(36), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("individual_profiles.id", ondelete="CASCADE"), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("company_id IS NOT NULL OR profile_id IS NOT NULL", name="ck_shortlist_target"),
    )
    op.create_index("idx_shortlists_user", "shortlists", ["user_id"])


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("shortlists")
    op.drop_table("admin_action_logs")
    op.drop_table("notifications")
    op.drop_table("review_flags")
    op.drop_table("reviews")
    op.drop_table("message_attachments")
    op.drop_table("messages")
    op.drop_table("message_participants")
    op.drop_table("message_threads")
    op.drop_table("rfq_status_history")
    op.drop_table("rfq_responses")
    op.drop_table("rfq_invitations")
    op.drop_table("rfq_attachments")
    op.drop_table("rfqs")
    op.drop_table("verification_documents")
    op.drop_table("verification_requests")
    op.drop_table("profile_media")
    op.drop_table("project_references")
    op.drop_table("certifications")
    op.drop_table("company_products")
    op.drop_table("company_services")
    op.drop_table("company_members")
    op.drop_table("individual_profiles")
    op.drop_table("companies")
    op.drop_table("service_categories")
    op.drop_table("product_categories")
    op.drop_table("governorates")
    op.drop_table("refresh_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_table("email_verification_tokens")
    op.drop_table("users")

    # Drop enum types
    sa.Enum(name="admin_action_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="notification_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="review_target_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="thread_context_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="rfq_response_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="rfq_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="verification_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="member_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="company_size").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="company_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="user_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="account_type").drop(op.get_bind(), checkfirst=True)
