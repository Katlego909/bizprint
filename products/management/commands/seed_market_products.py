from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from decimal import Decimal
from products.models import Product, Category, QuantityTier, ProductOption, OptionalService

class Command(BaseCommand):
    help = "Seed market-backed product data with competitive SA pricing."

    def handle(self, *args, **options):
        self.stdout.write("Seeding market products...")

        # 1. Define Categories
        categories = [
            "Business Cards",
            "Flyers & Leaflets",
            "Posters",
            "Banners & Signage",
            "Booklets & Magazines",
            "Stickers & Labels",
            "Calendars",
            "Corporate Gifts",
            "Apparel",
            "Stationery",
        ]

        cat_objs = {}
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"All your {cat_name} needs."}
            )
            cat_objs[cat_name] = cat
            if created:
                self.stdout.write(f"Created Category: {cat_name}")

        # 2. Define Products Data
        products_data = [
            # --- Business Cards ---
            {
                "name": "Standard Business Cards",
                "category": "Business Cards",
                "description": "Premium 350gsm board with a choice of finishes. The standard for professional networking.",
                "tiers": [
                    {"qty": 100, "price": 250},
                    {"qty": 250, "price": 350},
                    {"qty": 500, "price": 495},
                    {"qty": 1000, "price": 795},
                ],
                "options": [
                    {"type": "Finish", "value": "Matt Lamination", "price": 0},
                    {"type": "Finish", "value": "Gloss Lamination", "price": 0},
                    {"type": "Finish", "value": "Soft Touch", "price": 100},
                    {"type": "Sides", "value": "Single Sided", "price": 0},
                    {"type": "Sides", "value": "Double Sided", "price": 50},
                    {"type": "Corners", "value": "Square", "price": 0},
                    {"type": "Corners", "value": "Rounded", "price": 80},
                ],
                "services": [
                    {"label": "Design Service", "price": 250, "required": False},
                ]
            },
            {
                "name": "Spot UV Business Cards",
                "category": "Business Cards",
                "description": "Stand out with glossy raised areas on a matt background. Ultimate luxury.",
                "tiers": [
                    {"qty": 250, "price": 850},
                    {"qty": 500, "price": 1200},
                    {"qty": 1000, "price": 1800},
                ],
                "options": [
                    {"type": "Sides", "value": "Single Sided", "price": 0},
                    {"type": "Sides", "value": "Double Sided", "price": 150},
                ],
                "services": [
                    {"label": "Design Service", "price": 350, "required": False},
                ]
            },

            # --- Flyers ---
            {
                "name": "A5 Flyers (Gloss)",
                "category": "Flyers & Leaflets",
                "description": "128gsm Gloss paper. Perfect for handing out at events or street marketing.",
                "tiers": [
                    {"qty": 1000, "price": 999},
                    {"qty": 2500, "price": 1850},
                    {"qty": 5000, "price": 2999},
                ],
                "options": [
                    {"type": "Sides", "value": "Single Sided", "price": 0},
                    {"type": "Sides", "value": "Double Sided", "price": 200},
                ],
                "services": [
                    {"label": "Basic Layout", "price": 150, "required": False},
                ]
            },
            {
                "name": "A4 Folded Leaflets",
                "category": "Flyers & Leaflets",
                "description": "A4 folded to DL or A5. Great for menus and price lists. 170gsm Gloss.",
                "tiers": [
                    {"qty": 500, "price": 1450},
                    {"qty": 1000, "price": 2200},
                ],
                "options": [
                    {"type": "Fold", "value": "Z-Fold (Concertina)", "price": 0},
                    {"type": "Fold", "value": "Roll Fold", "price": 0},
                    {"type": "Fold", "value": "Half Fold", "price": 0},
                ],
                "services": []
            },

            # --- Posters ---
            {
                "name": "A1 Posters",
                "category": "Posters",
                "description": "Large format A1 posters printed on high quality satin paper.",
                "tiers": [
                    {"qty": 1, "price": 180},
                    {"qty": 5, "price": 800},
                    {"qty": 10, "price": 1500},
                ],
                "options": [
                    {"type": "Paper", "value": "Standard Satin", "price": 0},
                    {"type": "Paper", "value": "Premium Photo Gloss", "price": 50},
                ],
                "services": []
            },
            {
                "name": "A2 Posters",
                "category": "Posters",
                "description": "Medium format A2 posters. Great for indoor signage.",
                "tiers": [
                    {"qty": 5, "price": 450},
                    {"qty": 10, "price": 800},
                    {"qty": 50, "price": 3500},
                ],
                "options": [],
                "services": []
            },

            # --- Banners ---
            {
                "name": "Pull Up Banner (Standard)",
                "category": "Banners & Signage",
                "description": "850mm x 2000mm retractable banner stand. Includes carry bag.",
                "tiers": [
                    {"qty": 1, "price": 850},
                    {"qty": 2, "price": 1600},
                    {"qty": 5, "price": 3750},
                ],
                "options": [
                    {"type": "Base", "value": "Standard Silver", "price": 0},
                    {"type": "Base", "value": "Luxury Wide Base", "price": 300},
                ],
                "services": [
                    {"label": "Banner Design", "price": 450, "required": False},
                ]
            },
            {
                "name": "PVC Banners with Eyelets",
                "category": "Banners & Signage",
                "description": "Durable outdoor PVC banners. Price per square meter equivalent.",
                "tiers": [
                    {"qty": 1, "price": 350}, # representing a standard size like 2x1m roughly
                    {"qty": 5, "price": 1600},
                ],
                "options": [
                    {"type": "Size", "value": "2m x 1m", "price": 0},
                    {"type": "Size", "value": "3m x 1m", "price": 150},
                    {"type": "Size", "value": "3m x 2m", "price": 500},
                ],
                "services": []
            },

            # --- Stickers ---
            {
                "name": "Vinyl Stickers (Round)",
                "category": "Stickers & Labels",
                "description": "Waterproof vinyl stickers, kiss cut on sheets.",
                "tiers": [
                    {"qty": 100, "price": 350},
                    {"qty": 500, "price": 1200},
                    {"qty": 1000, "price": 1900},
                ],
                "options": [
                    {"type": "Size", "value": "30mm", "price": 0},
                    {"type": "Size", "value": "50mm", "price": 50},
                    {"type": "Size", "value": "80mm", "price": 150},
                ],
                "services": []
            },

            # --- Booklets ---
            {
                "name": "A4 Booklets (Saddle Stitched)",
                "category": "Booklets & Magazines",
                "description": "8 to 24 page booklets, stapled on the spine. Great for company profiles.",
                "tiers": [
                    {"qty": 50, "price": 2500},
                    {"qty": 100, "price": 4500},
                ],
                "options": [
                    {"type": "Pages", "value": "8 Pages", "price": 0},
                    {"type": "Pages", "value": "12 Pages", "price": 500},
                    {"type": "Pages", "value": "16 Pages", "price": 1000},
                ],
                "services": []
            },

            # --- Corporate Gifts ---
            {
                "name": "Branded Coffee Mugs",
                "category": "Corporate Gifts",
                "description": "Standard 330ml white ceramic mug with full colour sublimation print.",
                "tiers": [
                    {"qty": 10, "price": 850},
                    {"qty": 50, "price": 3750},
                    {"qty": 100, "price": 6500},
                ],
                "options": [],
                "services": []
            },
            {
                "name": "Branded Pens",
                "category": "Corporate Gifts",
                "description": "Plastic barrel pens with single colour pad print.",
                "tiers": [
                    {"qty": 100, "price": 800},
                    {"qty": 500, "price": 3500},
                ],
                "options": [
                    {"type": "Ink Colour", "value": "Black", "price": 0},
                    {"type": "Ink Colour", "value": "Blue", "price": 0},
                ],
                "services": []
            },
        ]

        # 3. Create Products and related data
        for p_data in products_data:
            cat = cat_objs.get(p_data["category"])
            
            # Create dummy image content
            dummy_image_content = b"fake_image_data"
            
            product, created = Product.objects.get_or_create(
                name=p_data["name"],
                defaults={
                    "category": cat,
                    "description": p_data["description"],
                }
            )
            
            # If created, we need to save the image file to satisfy the ImageField
            if created:
                # We save a dummy file. In production, you'd want real images.
                product.image.save(f"{slugify(p_data['name'])}.jpg", ContentFile(dummy_image_content), save=True)
                self.stdout.write(self.style.SUCCESS(f"Created Product: {product.name}"))
            else:
                self.stdout.write(f"Product already exists: {product.name}")

            # Create Quantity Tiers
            for tier in p_data["tiers"]:
                QuantityTier.objects.get_or_create(
                    product=product,
                    quantity=tier["qty"],
                    defaults={"base_price": Decimal(tier["price"])}
                )

            # Create Options
            for opt in p_data["options"]:
                ProductOption.objects.get_or_create(
                    product=product,
                    option_type=opt["type"],
                    value=opt["value"],
                    defaults={"price_modifier": Decimal(opt["price"])}
                )

            # Create Services
            for srv in p_data["services"]:
                OptionalService.objects.get_or_create(
                    product=product,
                    label=srv["label"],
                    defaults={
                        "price": Decimal(srv["price"]),
                        "is_required": srv.get("required", False)
                    }
                )

        self.stdout.write(self.style.SUCCESS("Market products seeded successfully!"))
