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
        # Full professional product data, matching seed_products.py, with robust category assignment
        products_data = [
            # --- Business Cards ---
            {
                "name": "Premium Business Cards",
                "category": "Business Cards",
                "description": "Premium 350gsm business cards with a choice of gloss or matte finish. Perfect for first impressions.",
                "image": "product_images/business_cards.jpg",
                "tiers": [
                    {"qty": 100, "price": 299},
                    {"qty": 250, "price": 499},
                    {"qty": 500, "price": 899},
                    {"qty": 1000, "price": 1499},
                ],
                "options": [
                    {"type": "Format", "value": "Single-Sided", "price": 0},
                    {"type": "Format", "value": "Double-Sided", "price": 50},
                    {"type": "Finish", "value": "Gloss", "price": 20},
                    {"type": "Finish", "value": "Matte", "price": 20},
                    {"type": "Paper", "value": "350gsm Premium", "price": 0},
                ],
                "services": [
                    {"label": "3-Day Design Service", "price": 200, "required": False},
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Eco Kraft Business Cards",
                "category": "Business Cards",
                "description": "Eco-friendly kraft business cards printed on 300gsm recycled board. A natural look for sustainable brands.",
                "image": "product_images/business_cards_kraft.jpg",
                "tiers": [
                    {"qty": 100, "price": 329},
                    {"qty": 250, "price": 529},
                    {"qty": 500, "price": 949},
                    {"qty": 1000, "price": 1599},
                ],
                "options": [
                    {"type": "Format", "value": "Single-Sided", "price": 0},
                    {"type": "Format", "value": "Double-Sided", "price": 40},
                    {"type": "Paper", "value": "300gsm Kraft", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Flyers ---
            {
                "name": "A5 Full Colour Flyers",
                "category": "Flyers & Leaflets",
                "description": "Vibrant A5 flyers printed on 130gsm gloss paper. Ideal for promotions and events.",
                "image": "product_images/flyers.jpg",
                "tiers": [
                    {"qty": 500, "price": 399},
                    {"qty": 1000, "price": 699},
                    {"qty": 2500, "price": 1499},
                    {"qty": 5000, "price": 2499},
                ],
                "options": [
                    {"type": "Size", "value": "A5", "price": 0},
                    {"type": "Size", "value": "A4", "price": 150},
                    {"type": "Paper", "value": "130gsm Gloss", "price": 0},
                    {"type": "Paper", "value": "170gsm Matte", "price": 50},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 149, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "DL Promotional Flyers",
                "category": "Flyers & Leaflets",
                "description": "DL size flyers (99x210mm) printed on 150gsm silk paper. Great for inserts and handouts.",
                "image": "product_images/flyers_dl.jpg",
                "tiers": [
                    {"qty": 500, "price": 349},
                    {"qty": 1000, "price": 599},
                    {"qty": 2500, "price": 1299},
                    {"qty": 5000, "price": 2199},
                ],
                "options": [
                    {"type": "Size", "value": "DL", "price": 0},
                    {"type": "Paper", "value": "150gsm Silk", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 149, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Brochures ---
            {
                "name": "A4 Tri-Fold Brochures",
                "category": "Stationery",
                "description": "A4 brochures folded to DL, printed on 170gsm gloss. Perfect for menus and company profiles.",
                "image": "product_images/brochures_trifold.jpg",
                "tiers": [
                    {"qty": 250, "price": 799},
                    {"qty": 500, "price": 1399},
                    {"qty": 1000, "price": 2499},
                ],
                "options": [
                    {"type": "Fold", "value": "Tri-Fold", "price": 0},
                    {"type": "Paper", "value": "170gsm Gloss", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 199, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "A5 Half-Fold Brochures",
                "category": "Stationery",
                "description": "A5 brochures folded to A6, printed on 150gsm matte. Ideal for event programs and mini-menus.",
                "image": "product_images/brochures_halffold.jpg",
                "tiers": [
                    {"qty": 250, "price": 599},
                    {"qty": 500, "price": 1099},
                    {"qty": 1000, "price": 1999},
                ],
                "options": [
                    {"type": "Fold", "value": "Half-Fold", "price": 0},
                    {"type": "Paper", "value": "150gsm Matte", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 199, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Posters ---
            {
                "name": "A2 Full Colour Posters",
                "category": "Posters",
                "description": "A2 posters printed on 200gsm satin paper. Eye-catching for events and promotions.",
                "image": "product_images/posters_a2.jpg",
                "tiers": [
                    {"qty": 10, "price": 299},
                    {"qty": 25, "price": 599},
                    {"qty": 50, "price": 999},
                ],
                "options": [
                    {"type": "Size", "value": "A2", "price": 0},
                    {"type": "Paper", "value": "200gsm Satin", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "A1 Promotional Posters",
                "category": "Posters",
                "description": "Large A1 posters printed on 170gsm gloss. Great for retail and advertising.",
                "image": "product_images/posters_a1.jpg",
                "tiers": [
                    {"qty": 5, "price": 249},
                    {"qty": 10, "price": 449},
                    {"qty": 25, "price": 849},
                ],
                "options": [
                    {"type": "Size", "value": "A1", "price": 0},
                    {"type": "Paper", "value": "170gsm Gloss", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Stickers ---
            {
                "name": "Round Vinyl Stickers",
                "category": "Stickers & Labels",
                "description": "Durable round vinyl stickers, 50mm diameter, waterproof and perfect for branding.",
                "image": "product_images/stickers_round.jpg",
                "tiers": [
                    {"qty": 100, "price": 199},
                    {"qty": 250, "price": 399},
                    {"qty": 500, "price": 699},
                ],
                "options": [
                    {"type": "Shape", "value": "Round", "price": 0},
                    {"type": "Material", "value": "Vinyl", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 49, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Square Paper Stickers",
                "category": "Stickers & Labels",
                "description": "Square stickers, 50x50mm, printed on gloss paper. Affordable for packaging and gifts.",
                "image": "product_images/stickers_square.jpg",
                "tiers": [
                    {"qty": 100, "price": 149},
                    {"qty": 250, "price": 299},
                    {"qty": 500, "price": 549},
                ],
                "options": [
                    {"type": "Shape", "value": "Square", "price": 0},
                    {"type": "Material", "value": "Gloss Paper", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 49, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- T-shirts ---
            {
                "name": "Classic White T-shirt",
                "category": "Apparel",
                "description": "100% cotton white t-shirt with custom full-colour print. Unisex fit.",
                "image": "product_images/tshirt_white.jpg",
                "tiers": [
                    {"qty": 10, "price": 799},
                    {"qty": 25, "price": 1799},
                    {"qty": 50, "price": 3299},
                ],
                "options": [
                    {"type": "Size", "value": "S", "price": 0},
                    {"type": "Size", "value": "M", "price": 0},
                    {"type": "Size", "value": "L", "price": 0},
                    {"type": "Size", "value": "XL", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Premium Black T-shirt",
                "category": "Apparel",
                "description": "Premium black t-shirt, 180gsm, with custom logo print. Soft and durable.",
                "image": "product_images/tshirt_black.jpg",
                "tiers": [
                    {"qty": 10, "price": 899},
                    {"qty": 25, "price": 1999},
                    {"qty": 50, "price": 3599},
                ],
                "options": [
                    {"type": "Size", "value": "S", "price": 0},
                    {"type": "Size", "value": "M", "price": 0},
                    {"type": "Size", "value": "L", "price": 0},
                    {"type": "Size", "value": "XL", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Uniforms ---
            {
                "name": "Classic Work Shirt",
                "category": "Apparel",
                "description": "Poly-cotton work shirt, available in navy or khaki. Embroidery option available.",
                "image": "product_images/uniforms_shirt.jpg",
                "tiers": [
                    {"qty": 5, "price": 499},
                    {"qty": 10, "price": 899},
                    {"qty": 25, "price": 1999},
                ],
                "options": [
                    {"type": "Colour", "value": "Navy", "price": 0},
                    {"type": "Colour", "value": "Khaki", "price": 0},
                ],
                "services": [
                    {"label": "Embroidery (per shirt)", "price": 50, "required": False},
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Chef Jacket",
                "category": "Apparel",
                "description": "Professional chef jacket, double-breasted, available in white or black.",
                "image": "product_images/uniforms_chef.jpg",
                "tiers": [
                    {"qty": 2, "price": 399},
                    {"qty": 5, "price": 899},
                    {"qty": 10, "price": 1699},
                ],
                "options": [
                    {"type": "Colour", "value": "White", "price": 0},
                    {"type": "Colour", "value": "Black", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 99, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Packaging ---
            {
                "name": "Custom Printed Boxes",
                "category": "Stationery",
                "description": "Corrugated boxes with full-colour print. Perfect for e-commerce and retail packaging.",
                "image": "product_images/packaging_boxes.jpg",
                "tiers": [
                    {"qty": 50, "price": 1499},
                    {"qty": 100, "price": 2599},
                    {"qty": 250, "price": 5999},
                ],
                "options": [
                    {"type": "Size", "value": "Small", "price": 0},
                    {"type": "Size", "value": "Medium", "price": 200},
                    {"type": "Size", "value": "Large", "price": 400},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 299, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Printed Paper Bags",
                "category": "Stationery",
                "description": "Recyclable paper bags with your logo. Great for retail and events.",
                "image": "product_images/packaging_bags.jpg",
                "tiers": [
                    {"qty": 100, "price": 799},
                    {"qty": 250, "price": 1799},
                    {"qty": 500, "price": 2999},
                ],
                "options": [
                    {"type": "Size", "value": "Small", "price": 0},
                    {"type": "Size", "value": "Large", "price": 150},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 149, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Corporate Gifts ---
            {
                "name": "Branded Metal Pens",
                "category": "Corporate Gifts",
                "description": "Metal ballpoint pens with laser engraving. Supplied in a gift box.",
                "image": "product_images/gifts_pens.jpg",
                "tiers": [
                    {"qty": 50, "price": 499},
                    {"qty": 100, "price": 899},
                    {"qty": 250, "price": 1999},
                ],
                "options": [
                    {"type": "Colour", "value": "Silver", "price": 0},
                    {"type": "Colour", "value": "Blue", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 49, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Custom Coffee Mugs",
                "category": "Corporate Gifts",
                "description": "Ceramic mugs with full-colour wrap print. Dishwasher safe.",
                "image": "product_images/gifts_mugs.jpg",
                "tiers": [
                    {"qty": 24, "price": 399},
                    {"qty": 48, "price": 749},
                    {"qty": 96, "price": 1399},
                ],
                "options": [
                    {"type": "Colour", "value": "White", "price": 0},
                    {"type": "Colour", "value": "Black", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 49, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            # --- Personalized Gifts ---
            {
                "name": "Photo Keyrings",
                "category": "Corporate Gifts",
                "description": "Acrylic keyrings with your custom photo. Great for events and giveaways.",
                "image": "product_images/personalized_keyrings.jpg",
                "tiers": [
                    {"qty": 20, "price": 199},
                    {"qty": 50, "price": 399},
                    {"qty": 100, "price": 749},
                ],
                "options": [
                    {"type": "Shape", "value": "Rectangle", "price": 0},
                    {"type": "Shape", "value": "Heart", "price": 10},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 49, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
            },
            {
                "name": "Custom Mouse Pads",
                "category": "Corporate Gifts",
                "description": "Personalized mouse pads with your image or logo. Non-slip rubber base.",
                "image": "product_images/personalized_mousepads.jpg",
                "tiers": [
                    {"qty": 10, "price": 249},
                    {"qty": 25, "price": 499},
                    {"qty": 50, "price": 899},
                ],
                "options": [
                    {"type": "Shape", "value": "Rectangle", "price": 0},
                    {"type": "Shape", "value": "Round", "price": 0},
                ],
                "services": [
                    {"label": "Express Delivery (1-2 days)", "price": 49, "required": False},
                    {"label": "Standard Delivery (3-5 days)", "price": 0, "required": False},
                ]
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
