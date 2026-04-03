"""
Seed product categories, service categories, and governorates.

Usage:
    python -m scripts.seed_categories
"""

import asyncio
import sys

from slugify import slugify

sys.path.insert(0, ".")

from app.database import async_session_factory
from app.models.category import Governorate, ProductCategory, ServiceCategory


PRODUCT_CATEGORIES = [
    {"name": "Fiber Optic Cables", "children": [
        "Single Mode Fiber Cable",
        "Multi Mode Fiber Cable",
        "ADSS Cable",
        "Aerial Cable",
        "Underground Cable",
        "Indoor Cable",
        "Drop Cable",
        "Ribbon Cable",
        "Armored Cable",
    ]},
    {"name": "Passive Components", "children": [
        "Fiber Patch Cords",
        "Pigtails",
        "Adapters / Couplers",
        "Attenuators",
        "Splitters (PLC)",
        "WDM Filters",
        "Fiber Connectors",
    ]},
    {"name": "Enclosures & Cabinets", "children": [
        "ODF (Optical Distribution Frame)",
        "Splice Closures",
        "Wall Mount Boxes",
        "Rack Mount Panels",
        "FDB (Fiber Distribution Box)",
        "FAT (Fiber Access Terminal)",
        "Street Cabinets",
        "Manholes & Handholes",
    ]},
    {"name": "Test & Measurement Equipment", "children": [
        "OTDR",
        "Optical Power Meter",
        "Light Source",
        "Visual Fault Locator (VFL)",
        "Fiber Identifier",
        "Optical Spectrum Analyzer",
        "Fiber Inspection Microscope",
    ]},
    {"name": "Tools & Accessories", "children": [
        "Fusion Splicer",
        "Mechanical Splicer",
        "Fiber Cleaver",
        "Fiber Stripper",
        "Cable Pulling Equipment",
        "Duct Rodder",
        "Blowing Machine",
        "HDPE Ducts & Subducts",
        "Cable Ties & Markers",
    ]},
    {"name": "Active Equipment", "children": [
        "OLT (Optical Line Terminal)",
        "ONU / ONT",
        "Media Converter",
        "SFP / SFP+ Modules",
        "Optical Amplifier (EDFA)",
    ]},
]

SERVICE_CATEGORIES = [
    {"name": "FTTH Services", "children": [
        "FTTH Design & Planning",
        "FTTH Installation",
        "FTTH Splicing",
        "FTTH Testing & Commissioning",
        "FTTH Maintenance",
        "Home Connectivity (Last Mile)",
    ]},
    {"name": "OSP Services", "children": [
        "OSP Route Survey",
        "OSP Design",
        "OSP Construction",
        "Aerial Installation",
        "Underground Installation",
        "Duct Installation",
        "Manhole & Handhole Installation",
        "Cable Pulling",
        "Cable Blowing",
    ]},
    {"name": "Splicing & Termination", "children": [
        "Fusion Splicing",
        "Mechanical Splicing",
        "Connector Termination",
        "Pigtail Termination",
        "ODF Termination",
    ]},
    {"name": "Testing & Commissioning", "children": [
        "OTDR Testing",
        "Power Level Testing",
        "End-to-End Testing",
        "Acceptance Testing",
        "As-Built Documentation",
    ]},
    {"name": "Civil Works", "children": [
        "Trenching",
        "Micro-Trenching",
        "HDD (Horizontal Directional Drilling)",
        "Duct Bank Construction",
        "Reinstatement",
    ]},
    {"name": "Maintenance & Support", "children": [
        "Preventive Maintenance",
        "Emergency Repair",
        "Fault Location",
        "Network Monitoring",
        "SLA-Based Maintenance",
    ]},
    {"name": "Consulting & Design", "children": [
        "Network Planning",
        "Feasibility Study",
        "BOQ Preparation",
        "Technical Specifications",
        "Project Management",
        "Quality Control / QA",
    ]},
]

GOVERNORATES = [
    ("Cairo", "القاهرة"),
    ("Giza", "الجيزة"),
    ("Alexandria", "الإسكندرية"),
    ("Qalyubia", "القليوبية"),
    ("Sharqia", "الشرقية"),
    ("Dakahlia", "الدقهلية"),
    ("Beheira", "البحيرة"),
    ("Monufia", "المنوفية"),
    ("Gharbia", "الغربية"),
    ("Kafr El Sheikh", "كفر الشيخ"),
    ("Damietta", "دمياط"),
    ("Port Said", "بورسعيد"),
    ("Ismailia", "الإسماعيلية"),
    ("Suez", "السويس"),
    ("Fayoum", "الفيوم"),
    ("Beni Suef", "بني سويف"),
    ("Minya", "المنيا"),
    ("Assiut", "أسيوط"),
    ("Sohag", "سوهاج"),
    ("Qena", "قنا"),
    ("Luxor", "الأقصر"),
    ("Aswan", "أسوان"),
    ("Red Sea", "البحر الأحمر"),
    ("North Sinai", "شمال سيناء"),
    ("South Sinai", "جنوب سيناء"),
    ("Matrouh", "مطروح"),
    ("New Valley", "الوادي الجديد"),
]


async def seed():
    async with async_session_factory() as db:
        # Seed product categories
        for parent_data in PRODUCT_CATEGORIES:
            parent = ProductCategory(
                name=parent_data["name"],
                slug=slugify(parent_data["name"]),
            )
            db.add(parent)
            await db.flush()

            for idx, child_name in enumerate(parent_data.get("children", [])):
                child = ProductCategory(
                    name=child_name,
                    slug=slugify(child_name),
                    parent_id=parent.id,
                    sort_order=idx,
                )
                db.add(child)

        # Seed service categories
        for parent_data in SERVICE_CATEGORIES:
            parent = ServiceCategory(
                name=parent_data["name"],
                slug=slugify(parent_data["name"]),
            )
            db.add(parent)
            await db.flush()

            for idx, child_name in enumerate(parent_data.get("children", [])):
                child = ServiceCategory(
                    name=child_name,
                    slug=slugify(child_name),
                    parent_id=parent.id,
                    sort_order=idx,
                )
                db.add(child)

        # Seed governorates
        for name, name_ar in GOVERNORATES:
            gov = Governorate(name=name, name_ar=name_ar)
            db.add(gov)

        await db.commit()
        print("Seed data inserted successfully.")
        print(f"  Product categories: {sum(1 + len(p.get('children', [])) for p in PRODUCT_CATEGORIES)}")
        print(f"  Service categories: {sum(1 + len(s.get('children', [])) for s in SERVICE_CATEGORIES)}")
        print(f"  Governorates: {len(GOVERNORATES)}")


if __name__ == "__main__":
    asyncio.run(seed())
