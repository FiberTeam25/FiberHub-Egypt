from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import (
    Certification,
    Company,
    CompanyMember,
    CompanyProduct,
    CompanyService,
    MemberRole,
    ProjectReference,
)


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, company: Company) -> Company:
        self.db.add(company)
        await self.db.flush()
        return company

    async def get_by_id(self, company_id: str) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.slug == slug))
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str) -> bool:
        result = await self.db.execute(
            select(func.count()).select_from(Company).where(Company.slug == slug)
        )
        return result.scalar_one() > 0

    async def list_companies(
        self,
        page: int = 1,
        page_size: int = 20,
        company_type: str | None = None,
        governorate: str | None = None,
        verified_only: bool = False,
        search: str | None = None,
    ) -> tuple[list[Company], int]:
        query = select(Company).where(Company.is_active.is_(True))
        count_query = select(func.count()).select_from(Company).where(Company.is_active.is_(True))

        if company_type:
            query = query.where(Company.company_type == company_type)
            count_query = count_query.where(Company.company_type == company_type)

        if governorate:
            query = query.where(Company.governorate == governorate)
            count_query = count_query.where(Company.governorate == governorate)

        if verified_only:
            query = query.where(Company.verification_status == "approved")
            count_query = count_query.where(Company.verification_status == "approved")

        if search:
            search_filter = Company.name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(Company.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total

    async def update(self, company: Company, **kwargs) -> Company:
        for key, value in kwargs.items():
            if value is not None and hasattr(company, key):
                setattr(company, key, value)
        await self.db.flush()
        return company

    # Members
    async def add_member(self, member: CompanyMember) -> CompanyMember:
        self.db.add(member)
        await self.db.flush()
        return member

    async def get_member(self, company_id: str, user_id: str) -> CompanyMember | None:
        result = await self.db.execute(
            select(CompanyMember)
            .options(selectinload(CompanyMember.user))
            .where(
                CompanyMember.company_id == company_id,
                CompanyMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_member_by_id(self, member_id: str) -> CompanyMember | None:
        result = await self.db.execute(
            select(CompanyMember)
            .options(selectinload(CompanyMember.user))
            .where(CompanyMember.id == member_id)
        )
        return result.scalar_one_or_none()

    async def list_members(self, company_id: str) -> list[CompanyMember]:
        result = await self.db.execute(
            select(CompanyMember)
            .options(selectinload(CompanyMember.user))
            .where(CompanyMember.company_id == company_id)
            .order_by(CompanyMember.joined_at)
        )
        return list(result.scalars().all())

    async def remove_member(self, member: CompanyMember) -> None:
        await self.db.delete(member)
        await self.db.flush()

    async def get_user_role_in_company(self, company_id: str, user_id: str) -> MemberRole | None:
        member = await self.get_member(company_id, user_id)
        return member.role if member else None

    # Services
    async def add_service(self, service: CompanyService) -> CompanyService:
        self.db.add(service)
        await self.db.flush()
        return service

    async def remove_service(self, service_id: str) -> None:
        result = await self.db.execute(
            select(CompanyService).where(CompanyService.id == service_id)
        )
        service = result.scalar_one_or_none()
        if service:
            await self.db.delete(service)
            await self.db.flush()

    # Products
    async def add_product(self, product: CompanyProduct) -> CompanyProduct:
        self.db.add(product)
        await self.db.flush()
        return product

    async def remove_product(self, product_id: str) -> None:
        result = await self.db.execute(
            select(CompanyProduct).where(CompanyProduct.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            await self.db.delete(product)
            await self.db.flush()

    # Certifications
    async def add_certification(self, cert: Certification) -> Certification:
        self.db.add(cert)
        await self.db.flush()
        return cert

    async def remove_certification(self, cert_id: str) -> None:
        result = await self.db.execute(
            select(Certification).where(Certification.id == cert_id)
        )
        cert = result.scalar_one_or_none()
        if cert:
            await self.db.delete(cert)
            await self.db.flush()

    # References
    async def add_reference(self, ref: ProjectReference) -> ProjectReference:
        self.db.add(ref)
        await self.db.flush()
        return ref

    async def remove_reference(self, ref_id: str) -> None:
        result = await self.db.execute(
            select(ProjectReference).where(ProjectReference.id == ref_id)
        )
        ref = result.scalar_one_or_none()
        if ref:
            await self.db.delete(ref)
            await self.db.flush()
