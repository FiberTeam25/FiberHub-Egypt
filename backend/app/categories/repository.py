from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Governorate, ProductCategory, ServiceCategory


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Product categories
    async def list_product_categories(self) -> list[ProductCategory]:
        result = await self.db.execute(
            select(ProductCategory)
            .where(ProductCategory.is_active.is_(True))
            .order_by(ProductCategory.sort_order, ProductCategory.name)
        )
        return list(result.scalars().all())

    async def get_product_category(self, cat_id: str) -> ProductCategory | None:
        result = await self.db.execute(
            select(ProductCategory).where(ProductCategory.id == cat_id)
        )
        return result.scalar_one_or_none()

    async def create_product_category(self, category: ProductCategory) -> ProductCategory:
        self.db.add(category)
        await self.db.flush()
        return category

    # Service categories
    async def list_service_categories(self) -> list[ServiceCategory]:
        result = await self.db.execute(
            select(ServiceCategory)
            .where(ServiceCategory.is_active.is_(True))
            .order_by(ServiceCategory.sort_order, ServiceCategory.name)
        )
        return list(result.scalars().all())

    async def get_service_category(self, cat_id: str) -> ServiceCategory | None:
        result = await self.db.execute(
            select(ServiceCategory).where(ServiceCategory.id == cat_id)
        )
        return result.scalar_one_or_none()

    async def create_service_category(self, category: ServiceCategory) -> ServiceCategory:
        self.db.add(category)
        await self.db.flush()
        return category

    # Governorates
    async def list_governorates(self) -> list[Governorate]:
        result = await self.db.execute(
            select(Governorate).order_by(Governorate.name)
        )
        return list(result.scalars().all())
