from slugify import slugify

from app.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models.company import (
    Certification,
    Company,
    CompanyMember,
    CompanyProduct,
    CompanyService,
    MemberRole,
    ProjectReference,
)
from app.models.user import User
from app.companies.repository import CompanyRepository


class CompanyService:
    def __init__(self, repo: CompanyRepository):
        self.repo = repo

    async def create_company(self, user: User, **kwargs) -> Company:
        name = kwargs["name"]
        slug = await self._generate_unique_slug(name)

        company = Company(slug=slug, **kwargs)
        company = await self.repo.create(company)

        # Add creator as owner
        member = CompanyMember(
            company_id=company.id,
            user_id=user.id,
            role=MemberRole.OWNER,
            is_primary=True,
        )
        await self.repo.add_member(member)

        company.profile_completion = self._calculate_completion(company)
        return company

    async def get_company_by_slug(self, slug: str) -> Company:
        company = await self.repo.get_by_slug(slug)
        if not company or not company.is_active:
            raise NotFoundError("Company not found")
        return company

    async def get_company_by_id(self, company_id: str) -> Company:
        company = await self.repo.get_by_id(company_id)
        if not company:
            raise NotFoundError("Company not found")
        return company

    async def list_companies(self, **filters) -> tuple[list[Company], int]:
        return await self.repo.list_companies(**filters)

    async def update_company(self, company_id: str, user: User, **kwargs) -> Company:
        company = await self.get_company_by_id(company_id)
        await self._require_company_admin(company_id, user)

        # Regenerate slug if name changed
        if kwargs.get("name") and kwargs["name"] != company.name:
            kwargs["slug"] = await self._generate_unique_slug(kwargs["name"])

        company = await self.repo.update(company, **kwargs)
        company.profile_completion = self._calculate_completion(company)
        return company

    # --- Members ---

    async def list_members(self, company_id: str) -> list[CompanyMember]:
        await self.get_company_by_id(company_id)
        return await self.repo.list_members(company_id)

    async def add_member(
        self, company_id: str, user: User, target_user: User, role: MemberRole, title: str | None
    ) -> CompanyMember:
        await self._require_company_admin(company_id, user)

        existing = await self.repo.get_member(company_id, target_user.id)
        if existing:
            raise ConflictError("User is already a member of this company")

        member = CompanyMember(
            company_id=company_id,
            user_id=target_user.id,
            role=role,
            title=title,
        )
        return await self.repo.add_member(member)

    async def update_member(
        self, company_id: str, member_id: str, user: User, **kwargs
    ) -> CompanyMember:
        await self._require_company_admin(company_id, user)
        member = await self.repo.get_member_by_id(member_id)
        if not member or member.company_id != company_id:
            raise NotFoundError("Member not found")
        if member.role == MemberRole.OWNER:
            raise ForbiddenError("Cannot modify the owner's role")

        for key, value in kwargs.items():
            if value is not None and hasattr(member, key):
                setattr(member, key, value)
        await self.repo.db.flush()
        return member

    async def remove_member(self, company_id: str, member_id: str, user: User) -> None:
        await self._require_company_admin(company_id, user)
        member = await self.repo.get_member_by_id(member_id)
        if not member or member.company_id != company_id:
            raise NotFoundError("Member not found")
        if member.role == MemberRole.OWNER:
            raise ForbiddenError("Cannot remove the company owner")
        await self.repo.remove_member(member)

    # --- Services / Products / Certs / References ---

    async def add_service(
        self, company_id: str, user: User, service_category_id: str, description: str | None
    ) -> CompanyService:
        await self._require_company_admin(company_id, user)
        service = CompanyService(
            company_id=company_id,
            service_category_id=service_category_id,
            description=description,
        )
        return await self.repo.add_service(service)

    async def remove_service(self, company_id: str, service_id: str, user: User) -> None:
        await self._require_company_admin(company_id, user)
        await self.repo.remove_service(service_id)

    async def add_product(
        self, company_id: str, user: User, product_category_id: str,
        brand_names: list[str] | None, description: str | None,
    ) -> CompanyProduct:
        await self._require_company_admin(company_id, user)
        product = CompanyProduct(
            company_id=company_id,
            product_category_id=product_category_id,
            brand_names=brand_names,
            description=description,
        )
        return await self.repo.add_product(product)

    async def remove_product(self, company_id: str, product_id: str, user: User) -> None:
        await self._require_company_admin(company_id, user)
        await self.repo.remove_product(product_id)

    async def add_certification(
        self, company_id: str, user: User, **kwargs
    ) -> Certification:
        await self._require_company_admin(company_id, user)
        cert = Certification(company_id=company_id, **kwargs)
        return await self.repo.add_certification(cert)

    async def remove_certification(self, company_id: str, cert_id: str, user: User) -> None:
        await self._require_company_admin(company_id, user)
        await self.repo.remove_certification(cert_id)

    async def add_reference(
        self, company_id: str, user: User, **kwargs
    ) -> ProjectReference:
        await self._require_company_admin(company_id, user)
        ref = ProjectReference(company_id=company_id, **kwargs)
        return await self.repo.add_reference(ref)

    async def remove_reference(self, company_id: str, ref_id: str, user: User) -> None:
        await self._require_company_admin(company_id, user)
        await self.repo.remove_reference(ref_id)

    # --- Helpers ---

    async def _require_company_admin(self, company_id: str, user: User) -> None:
        if user.is_admin:
            return
        role = await self.repo.get_user_role_in_company(company_id, user.id)
        if role not in (MemberRole.OWNER, MemberRole.ADMIN):
            raise ForbiddenError("You must be a company owner or admin to perform this action")

    async def _generate_unique_slug(self, name: str) -> str:
        base_slug = slugify(name, max_length=200)
        slug = base_slug
        counter = 1
        while await self.repo.slug_exists(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    @staticmethod
    def _calculate_completion(company: Company) -> int:
        fields = [
            company.name,
            company.description,
            company.email,
            company.phone,
            company.address,
            company.city,
            company.governorate,
            company.company_size,
            company.year_established,
            company.logo_url,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)
