from slugify import slugify

from app.exceptions import NotFoundError
from app.models.category import Governorate, ProductCategory, ServiceCategory
from app.categories.repository import CategoryRepository


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def list_product_categories(self) -> list[ProductCategory]:
        return await self.repo.list_product_categories()

    async def list_service_categories(self) -> list[ServiceCategory]:
        return await self.repo.list_service_categories()

    async def list_governorates(self) -> list[Governorate]:
        return await self.repo.list_governorates()

    async def create_product_category(self, name: str, **kwargs) -> ProductCategory:
        category = ProductCategory(name=name, slug=slugify(name), **kwargs)
        return await self.repo.create_product_category(category)

    async def create_service_category(self, name: str, **kwargs) -> ServiceCategory:
        category = ServiceCategory(name=name, slug=slugify(name), **kwargs)
        return await self.repo.create_service_category(category)

    async def update_product_category(self, cat_id: str, **kwargs) -> ProductCategory:
        cat = await self.repo.get_product_category(cat_id)
        if not cat:
            raise NotFoundError("Product category not found")
        for key, value in kwargs.items():
            if value is not None and hasattr(cat, key):
                setattr(cat, key, value)
        if "name" in kwargs and kwargs["name"]:
            cat.slug = slugify(kwargs["name"])
        return cat

    async def update_service_category(self, cat_id: str, **kwargs) -> ServiceCategory:
        cat = await self.repo.get_service_category(cat_id)
        if not cat:
            raise NotFoundError("Service category not found")
        for key, value in kwargs.items():
            if value is not None and hasattr(cat, key):
                setattr(cat, key, value)
        if "name" in kwargs and kwargs["name"]:
            cat.slug = slugify(kwargs["name"])
        return cat
