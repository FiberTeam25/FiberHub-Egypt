"""
Seed fake users, companies, RFQs, messages, reviews, and verifications for development testing.

Prerequisites:
    python -m scripts.seed_categories   (for product/service category lookups)

Usage:
    python -m scripts.seed_fake_data
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")

import app.models  # noqa: F401 — registers all ORM models

from slugify import slugify
from sqlalchemy import select

from app.auth.utils import hash_password
from app.database import async_session_factory
from app.models.category import ProductCategory, ServiceCategory
from app.models.company import (
    Certification,
    Company,
    CompanyMember,
    CompanyProduct,
    CompanyService,
    CompanySize,
    CompanyType,
    MemberRole,
    ProjectReference,
    VerificationStatusEnum,
)
from app.models.message import Message, MessageParticipant, MessageThread, ThreadContextType
from app.models.profile import IndividualProfile
from app.models.review import Review, ReviewTargetType
from app.models.rfq import (
    RFQ,
    RFQInvitation,
    RFQResponse,
    RFQResponseStatus,
    RFQStatus,
    RFQStatusHistory,
)
from app.models.user import AccountType, User, UserStatus
from app.models.verification import VerificationDocument, VerificationRequest

# ---------------------------------------------------------------------------
# Static definitions
# ---------------------------------------------------------------------------

SEED_PASSWORD = "Test1234!"

SEED_USERS = [
    {
        "email": "buyer1@test.com",
        "first_name": "Ahmed",
        "last_name": "Hassan",
        "account_type": AccountType.BUYER,
        "phone": "+201001234501",
    },
    {
        "email": "buyer2@test.com",
        "first_name": "Sara",
        "last_name": "Mahmoud",
        "account_type": AccountType.BUYER,
        "phone": "+201001234502",
    },
    {
        "email": "supplier1@test.com",
        "first_name": "Khaled",
        "last_name": "Ibrahim",
        "account_type": AccountType.SUPPLIER,
        "phone": "+201001234503",
    },
    {
        "email": "supplier2@test.com",
        "first_name": "Mona",
        "last_name": "Ali",
        "account_type": AccountType.DISTRIBUTOR,
        "phone": "+201001234504",
    },
    {
        "email": "contractor1@test.com",
        "first_name": "Omar",
        "last_name": "Farouk",
        "account_type": AccountType.CONTRACTOR,
        "phone": "+201001234505",
    },
    {
        "email": "individual1@test.com",
        "first_name": "Laila",
        "last_name": "Nasser",
        "account_type": AccountType.INDIVIDUAL,
        "phone": "+201001234506",
    },
    {
        "email": "member1@test.com",
        "first_name": "Tarek",
        "last_name": "Saleh",
        "account_type": AccountType.SUPPLIER,
        "phone": "+201001234507",
    },
]

SEED_COMPANIES = [
    {
        "owner_email": "buyer1@test.com",
        "name": "Cairo Telecom Solutions",
        "company_type": CompanyType.BUYER,
        "description": "Leading telecom solutions provider in Greater Cairo specializing in fiber infrastructure projects.",
        "email": "info@cairotelecom.eg",
        "phone": "+20223456789",
        "address": "15 Nasr City Business District",
        "city": "Cairo",
        "governorate": "Cairo",
        "company_size": CompanySize.SIZE_51_200,
        "year_established": 2010,
        "commercial_reg_no": "CR-2010-001234",
        "tax_id": "TX-456789",
        "logo_url": "https://placehold.co/200x200?text=CTS",
        "website": "https://cairotelecom.eg",
    },
    {
        "owner_email": "buyer2@test.com",
        "name": "Alexandria Networks",
        "company_type": CompanyType.BUYER,
        "description": "Alexandria-based network operator expanding fiber coverage across the Mediterranean coast.",
        "email": "contact@alexnetworks.eg",
        "phone": "+20345678901",
        "address": "47 Corniche Road, Sporting",
        "city": "Alexandria",
        "governorate": "Alexandria",
        "company_size": CompanySize.SIZE_11_50,
        "year_established": 2015,
        "logo_url": "https://placehold.co/200x200?text=AN",
    },
    {
        "owner_email": "supplier1@test.com",
        "name": "FiberTech Egypt",
        "company_type": CompanyType.SUPPLIER,
        "description": "Premier fiber optic equipment supplier and systems integrator. ISO 9001 certified.",
        "email": "sales@fibertech.eg",
        "phone": "+20212345678",
        "address": "Industrial Zone, 6th of October City",
        "city": "6th of October",
        "governorate": "Giza",
        "company_size": CompanySize.SIZE_51_200,
        "year_established": 2005,
        "commercial_reg_no": "CR-2005-009876",
        "tax_id": "TX-123456",
        "logo_url": "https://placehold.co/200x200?text=FTE",
        "website": "https://fibertech.eg",
        "verification_status": VerificationStatusEnum.APPROVED,
    },
    {
        "owner_email": "supplier2@test.com",
        "name": "Nile Fiber Distribution",
        "company_type": CompanyType.DISTRIBUTOR,
        "description": "Authorized distributor of major international fiber optic brands across Upper and Lower Egypt.",
        "email": "info@nilefiberdist.eg",
        "phone": "+20224567890",
        "address": "Port Said Street, Heliopolis",
        "city": "Cairo",
        "governorate": "Cairo",
        "company_size": CompanySize.SIZE_11_50,
        "year_established": 2012,
        "logo_url": "https://placehold.co/200x200?text=NFD",
    },
    {
        "owner_email": "contractor1@test.com",
        "name": "Delta Construction Contractors",
        "company_type": CompanyType.CONTRACTOR,
        "description": "Specialized civil and OSP contractor for fiber optic infrastructure in the Nile Delta region.",
        "email": "projects@deltacc.eg",
        "phone": "+20504321098",
        "address": "New Mansoura, Dakahlia",
        "city": "Mansoura",
        "governorate": "Dakahlia",
        "company_size": CompanySize.SIZE_51_200,
        "year_established": 2008,
        "logo_url": "https://placehold.co/200x200?text=DCC",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def seed_users(db) -> dict[str, User]:
    """Create all seed users. Returns dict keyed by email."""
    users = {}
    for u in SEED_USERS:
        result = await db.execute(select(User).where(User.email == u["email"]))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  [skip] User already exists: {u['email']}")
            users[u["email"]] = existing
            continue
        user = User(
            email=u["email"],
            password_hash=hash_password(SEED_PASSWORD),
            first_name=u["first_name"],
            last_name=u["last_name"],
            account_type=u["account_type"],
            phone=u.get("phone"),
            email_verified=True,
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        await db.flush()
        users[u["email"]] = user
        print(f"  [created] User: {u['email']}")
    return users


async def seed_companies(db, users: dict) -> dict[str, Company]:
    """Create companies and add owners as primary members."""
    companies = {}
    for c in SEED_COMPANIES:
        owner = users.get(c["owner_email"])
        if not owner:
            print(f"  [skip] Owner not found for: {c['name']}")
            continue

        slug = slugify(c["name"], max_length=200)
        result = await db.execute(select(Company).where(Company.slug == slug))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  [skip] Company already exists: {c['name']}")
            companies[c["name"]] = existing
            continue

        kwargs = {k: v for k, v in c.items() if k != "owner_email"}
        company = Company(slug=slug, is_active=True, **kwargs)
        db.add(company)
        await db.flush()

        member = CompanyMember(
            company_id=company.id,
            user_id=owner.id,
            role=MemberRole.OWNER,
            is_primary=True,
        )
        db.add(member)
        await db.flush()

        companies[c["name"]] = company
        print(f"  [created] Company: {c['name']}")
    return companies


async def seed_company_extras(db, users: dict, companies: dict) -> None:
    """Add member, service, product, certification, and reference to FiberTech Egypt."""
    fibertech = companies.get("FiberTech Egypt")
    member1_user = users.get("member1@test.com")

    if not fibertech or not member1_user:
        print("  [skip] Missing FiberTech Egypt or member1 user")
        return

    # Add member1 as manager
    result = await db.execute(
        select(CompanyMember).where(
            CompanyMember.company_id == fibertech.id,
            CompanyMember.user_id == member1_user.id,
        )
    )
    if not result.scalar_one_or_none():
        db.add(CompanyMember(
            company_id=fibertech.id,
            user_id=member1_user.id,
            role=MemberRole.MANAGER,
            title="Sales Manager",
            is_primary=False,
        ))
        await db.flush()
        print("  [created] member1 added to FiberTech Egypt as Sales Manager")

    # Add service if category exists
    svc_result = await db.execute(
        select(ServiceCategory).where(ServiceCategory.slug == "ftth-installation")
    )
    svc_cat = svc_result.scalar_one_or_none()
    if svc_cat:
        result = await db.execute(
            select(CompanyService).where(
                CompanyService.company_id == fibertech.id,
                CompanyService.service_category_id == svc_cat.id,
            )
        )
        if not result.scalar_one_or_none():
            db.add(CompanyService(
                company_id=fibertech.id,
                service_category_id=svc_cat.id,
                description="Full FTTH deployment from OLT to subscriber premises, including civil works.",
            ))
            await db.flush()
            print("  [created] FiberTech Egypt: FTTH Installation service")
    else:
        # Fallback: use first available service category
        svc_result = await db.execute(select(ServiceCategory).limit(1))
        svc_cat = svc_result.scalar_one_or_none()
        if svc_cat:
            result = await db.execute(
                select(CompanyService).where(
                    CompanyService.company_id == fibertech.id,
                    CompanyService.service_category_id == svc_cat.id,
                )
            )
            if not result.scalar_one_or_none():
                db.add(CompanyService(
                    company_id=fibertech.id,
                    service_category_id=svc_cat.id,
                    description="Fiber optic installation and integration services.",
                ))
                await db.flush()
                print(f"  [created] FiberTech Egypt: service using category '{svc_cat.name}'")

    # Add product if category exists
    prod_result = await db.execute(
        select(ProductCategory).where(ProductCategory.slug == "single-mode-fiber-cable")
    )
    prod_cat = prod_result.scalar_one_or_none()
    if not prod_cat:
        prod_result = await db.execute(select(ProductCategory).limit(1))
        prod_cat = prod_result.scalar_one_or_none()

    if prod_cat:
        result = await db.execute(
            select(CompanyProduct).where(
                CompanyProduct.company_id == fibertech.id,
                CompanyProduct.product_category_id == prod_cat.id,
            )
        )
        if not result.scalar_one_or_none():
            db.add(CompanyProduct(
                company_id=fibertech.id,
                product_category_id=prod_cat.id,
                brand_names=["Corning", "Prysmian", "Furukawa"],
                description="G.652.D compliant single mode fiber cables, available in 2–144 core configurations.",
            ))
            await db.flush()
            print(f"  [created] FiberTech Egypt: product using category '{prod_cat.name}'")

    # Add ISO certification
    result = await db.execute(
        select(Certification).where(
            Certification.company_id == fibertech.id,
            Certification.name == "ISO 9001:2015",
        )
    )
    if not result.scalar_one_or_none():
        db.add(Certification(
            company_id=fibertech.id,
            name="ISO 9001:2015",
            issuing_body="Bureau Veritas",
            issue_date="2022-03-15",
            expiry_date="2025-03-14",
            document_url="https://placehold.co/cert/iso9001.pdf",
        ))
        await db.flush()
        print("  [created] FiberTech Egypt: ISO 9001:2015 certification")

    # Add project reference
    result = await db.execute(
        select(ProjectReference).where(
            ProjectReference.company_id == fibertech.id,
            ProjectReference.project_name == "Cairo Ring Network Phase 2",
        )
    )
    if not result.scalar_one_or_none():
        db.add(ProjectReference(
            company_id=fibertech.id,
            project_name="Cairo Ring Network Phase 2",
            client_name="Telecom Egypt",
            description="Supply and installation of 500km of G.652.D single mode fiber for metropolitan ring.",
            location="Greater Cairo",
            year=2022,
            scope="Design, supply, installation, testing, and commissioning",
        ))
        await db.flush()
        print("  [created] FiberTech Egypt: project reference 'Cairo Ring Network Phase 2'")


async def seed_individual_profile(db, users: dict) -> IndividualProfile | None:
    individual = users.get("individual1@test.com")
    if not individual:
        return None

    result = await db.execute(
        select(IndividualProfile).where(IndividualProfile.user_id == individual.id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        print("  [skip] Individual profile already exists")
        return existing

    slug = f"laila-nasser-{individual.id[:8]}"
    profile = IndividualProfile(
        user_id=individual.id,
        slug=slug,
        headline="Certified Fiber Optic Splicing Specialist",
        bio=(
            "10+ years of hands-on experience in fusion splicing, OTDR testing, "
            "and FTTH deployment across Egypt. Certified by Corning and Furukawa."
        ),
        specializations=["Fusion Splicing", "OTDR Testing", "FTTH Installation", "OSP Survey"],
        experience_years=10,
        city="Giza",
        governorate="Giza",
        availability="available",
        hourly_rate_egp=350.00,
        profile_completion=80,
    )
    db.add(profile)
    await db.flush()
    print("  [created] Individual profile: Laila Nasser")
    return profile


async def seed_rfq_workflow(db, users: dict, companies: dict) -> RFQ | None:
    """Create an open RFQ with an invitation and a submitted response."""
    buyer1_company = companies.get("Cairo Telecom Solutions")
    fibertech = companies.get("FiberTech Egypt")
    buyer1_user = users.get("buyer1@test.com")
    supplier1_user = users.get("supplier1@test.com")

    if not all([buyer1_company, fibertech, buyer1_user, supplier1_user]):
        print("  [skip] Missing entities for open RFQ workflow")
        return None

    result = await db.execute(
        select(RFQ).where(
            RFQ.company_id == buyer1_company.id,
            RFQ.title == "Supply of Single Mode Fiber Cable - 200km",
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        print("  [skip] Open RFQ already exists")
        return existing

    deadline = datetime.now(timezone.utc) + timedelta(days=30)

    rfq = RFQ(
        company_id=buyer1_company.id,
        created_by=buyer1_user.id,
        title="Supply of Single Mode Fiber Cable - 200km",
        request_type="product",
        description=(
            "Cairo Telecom Solutions requires 200km of G.652.D compliant single mode fiber cable "
            "for Phase 3 of the Cairo metropolitan network expansion. Cables must meet ITU-T G.652.D "
            "specifications, available in 48-core configuration with loose tube design."
        ),
        location="Cairo Industrial Zone, 10th of Ramadan City",
        governorate="Cairo",
        quantity_scope="200km total, minimum lot size 20km drums",
        timeline="Delivery within 8 weeks of PO issuance",
        deadline=deadline,
        notes="Preference for locally stocked items. Technical data sheets required with quotation.",
        status=RFQStatus.OPEN,
    )
    db.add(rfq)
    await db.flush()

    db.add(RFQStatusHistory(
        rfq_id=rfq.id,
        old_status=None,
        new_status=RFQStatus.DRAFT,
        changed_by=buyer1_user.id,
        note="RFQ created",
    ))
    db.add(RFQStatusHistory(
        rfq_id=rfq.id,
        old_status=RFQStatus.DRAFT,
        new_status=RFQStatus.OPEN,
        changed_by=buyer1_user.id,
        note="RFQ published",
    ))
    await db.flush()

    invitation = RFQInvitation(
        rfq_id=rfq.id,
        company_id=fibertech.id,
        status=RFQResponseStatus.SUBMITTED,
        invited_at=datetime.now(timezone.utc),
        viewed_at=datetime.now(timezone.utc),
    )
    db.add(invitation)
    await db.flush()

    response = RFQResponse(
        rfq_id=rfq.id,
        company_id=fibertech.id,
        submitted_by=supplier1_user.id,
        cover_note=(
            "FiberTech Egypt is pleased to offer G.652.D single mode fiber from Corning and Prysmian. "
            "We have 150km in stock at our 6th October warehouse and can source the remainder within 2 weeks."
        ),
        quoted_amount=2850000.00,
        currency="EGP",
        delivery_time="6 weeks from PO (stock items in 2 weeks)",
        notes="Price includes delivery to site. Payment terms: 30% advance, 70% on delivery.",
        status=RFQResponseStatus.SUBMITTED,
    )
    db.add(response)
    await db.flush()

    print(f"  [created] Open RFQ: '{rfq.title}' (ID: {rfq.id})")
    return rfq


async def seed_awarded_rfq(db, users: dict, companies: dict) -> None:
    """Create a completed, awarded RFQ to show the full lifecycle."""
    buyer2_company = companies.get("Alexandria Networks")
    nile_fiber = companies.get("Nile Fiber Distribution")
    buyer2_user = users.get("buyer2@test.com")
    supplier2_user = users.get("supplier2@test.com")

    if not all([buyer2_company, nile_fiber, buyer2_user, supplier2_user]):
        print("  [skip] Missing entities for awarded RFQ")
        return

    result = await db.execute(
        select(RFQ).where(
            RFQ.company_id == buyer2_company.id,
            RFQ.title == "OSP Survey Services - Alexandria Eastern Zone",
        )
    )
    if result.scalar_one_or_none():
        print("  [skip] Awarded RFQ already exists")
        return

    rfq = RFQ(
        company_id=buyer2_company.id,
        created_by=buyer2_user.id,
        title="OSP Survey Services - Alexandria Eastern Zone",
        request_type="service",
        description=(
            "Route survey, design, and BOQ preparation for 50km OSP network "
            "in Alexandria Eastern Zone. Includes 15 handhole locations."
        ),
        location="Eastern Alexandria",
        governorate="Alexandria",
        quantity_scope="50km route survey including 15 HH locations",
        timeline="Survey to be completed within 3 weeks",
        deadline=datetime.now(timezone.utc) - timedelta(days=10),
        status=RFQStatus.AWARDED,
        awarded_to=nile_fiber.id,
    )
    db.add(rfq)
    await db.flush()

    for old, new, note in [
        (None, RFQStatus.DRAFT, "Created"),
        (RFQStatus.DRAFT, RFQStatus.OPEN, "Published"),
        (RFQStatus.OPEN, RFQStatus.CLOSED, "Deadline passed"),
        (RFQStatus.CLOSED, RFQStatus.AWARDED, "Awarded to Nile Fiber Distribution"),
    ]:
        db.add(RFQStatusHistory(
            rfq_id=rfq.id,
            old_status=old,
            new_status=new,
            changed_by=buyer2_user.id,
            note=note,
        ))
    await db.flush()
    print(f"  [created] Awarded RFQ: '{rfq.title}'")


async def seed_message_thread(db, users: dict, rfq: RFQ | None) -> None:
    """Create a 4-message conversation between buyer and supplier about the open RFQ."""
    buyer1_user = users.get("buyer1@test.com")
    supplier1_user = users.get("supplier1@test.com")
    if not buyer1_user or not supplier1_user:
        return

    result = await db.execute(
        select(MessageThread).where(
            MessageThread.subject == "Re: Single Mode Fiber Cable RFQ - Technical Questions"
        )
    )
    if result.scalar_one_or_none():
        print("  [skip] Message thread already exists")
        return

    thread = MessageThread(
        context_type=ThreadContextType.RFQ,
        context_id=rfq.id if rfq else None,
        subject="Re: Single Mode Fiber Cable RFQ - Technical Questions",
    )
    db.add(thread)
    await db.flush()

    for user in [buyer1_user, supplier1_user]:
        db.add(MessageParticipant(thread_id=thread.id, user_id=user.id))
    await db.flush()

    conversation = [
        (
            buyer1_user,
            "Hello FiberTech team, could you confirm whether the Corning cables you quoted are "
            "the G.652.D variant? We need OS2 compliant cables specifically.",
        ),
        (
            supplier1_user,
            "Good afternoon Ahmed, yes all Corning cables we supply are G.652.D (OS2) compliant. "
            "We can provide test certificates and spec sheets. Would you like us to email them separately?",
        ),
        (
            buyer1_user,
            "Yes please, send them to procurement@cairotelecom.eg. Also, can you accommodate "
            "delivery to our warehouse in 10th of Ramadan City instead of site delivery?",
        ),
        (
            supplier1_user,
            "Absolutely. We have a regular delivery route to 10th of Ramadan. "
            "No additional charge for warehouse delivery. I'll arrange the spec sheets to be emailed today.",
        ),
    ]

    for sender, content in conversation:
        db.add(Message(thread_id=thread.id, sender_id=sender.id, content=content))
    await db.flush()
    print(f"  [created] Message thread with {len(conversation)} messages (ID: {thread.id})")


async def seed_review(db, users: dict, companies: dict, rfq: RFQ | None) -> None:
    """buyer1 leaves a 5-star review for FiberTech Egypt."""
    buyer1_user = users.get("buyer1@test.com")
    buyer1_company = companies.get("Cairo Telecom Solutions")
    fibertech = companies.get("FiberTech Egypt")
    if not all([buyer1_user, buyer1_company, fibertech]):
        return

    result = await db.execute(
        select(Review).where(
            Review.reviewer_id == buyer1_user.id,
            Review.target_company_id == fibertech.id,
        )
    )
    if result.scalar_one_or_none():
        print("  [skip] Review already exists")
        return

    db.add(Review(
        reviewer_id=buyer1_user.id,
        reviewer_company_id=buyer1_company.id,
        target_type=ReviewTargetType.COMPANY,
        target_company_id=fibertech.id,
        rfq_id=rfq.id if rfq else None,
        overall_rating=5,
        response_speed=5,
        communication=4,
        documentation=5,
        comment=(
            "FiberTech Egypt delivered exactly what they promised. "
            "The Corning G.652.D cables were delivered on schedule with full documentation. "
            "Their technical team was responsive and professional throughout. Highly recommended."
        ),
        is_visible=True,
    ))
    await db.flush()
    print("  [created] Review: buyer1 reviewed FiberTech Egypt (5 stars)")


async def seed_verification(db, companies: dict) -> None:
    """Submit a pending verification request for Nile Fiber Distribution."""
    nile_fiber = companies.get("Nile Fiber Distribution")
    if not nile_fiber:
        return

    result = await db.execute(
        select(VerificationRequest).where(VerificationRequest.company_id == nile_fiber.id)
    )
    if result.scalar_one_or_none():
        print("  [skip] Verification request already exists")
        return

    nile_fiber.verification_status = VerificationStatusEnum.PENDING

    verif = VerificationRequest(
        company_id=nile_fiber.id,
        status=VerificationStatusEnum.PENDING,
    )
    db.add(verif)
    await db.flush()

    for doc_type, file_name in [
        ("commercial_registration", "commercial_reg_nile_fiber.pdf"),
        ("tax_card", "tax_card_nile_fiber.pdf"),
    ]:
        db.add(VerificationDocument(
            verification_request_id=verif.id,
            document_type=doc_type,
            file_url=f"https://placehold.co/docs/{file_name}",
            file_name=file_name,
        ))
    await db.flush()
    print(f"  [created] Verification request for Nile Fiber Distribution (pending, ID: {verif.id})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed():
    print("=" * 60)
    print("FiberHub Egypt — Fake Data Seed")
    print("=" * 60)

    async with async_session_factory() as db:
        print("\n[1/8] Seeding users...")
        users = await seed_users(db)

        print("\n[2/8] Seeding companies...")
        companies = await seed_companies(db, users)

        print("\n[3/8] Seeding company extras (FiberTech Egypt)...")
        await seed_company_extras(db, users, companies)

        print("\n[4/8] Seeding individual profile...")
        await seed_individual_profile(db, users)

        print("\n[5/8] Seeding open RFQ workflow (Cairo Telecom → FiberTech)...")
        rfq = await seed_rfq_workflow(db, users, companies)

        print("\n[6/8] Seeding awarded RFQ (Alexandria Networks → Nile Fiber)...")
        await seed_awarded_rfq(db, users, companies)

        print("\n[7/8] Seeding message thread...")
        await seed_message_thread(db, users, rfq)

        print("\n[8/8] Seeding review + verification request...")
        await seed_review(db, users, companies, rfq)
        await seed_verification(db, companies)

        await db.commit()

    print("\n" + "=" * 60)
    print("Seed complete!")
    print(f"Password for all test accounts: {SEED_PASSWORD}")
    print("\nTest accounts:")
    for u in SEED_USERS:
        print(f"  {u['account_type'].value:<15}  {u['email']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
