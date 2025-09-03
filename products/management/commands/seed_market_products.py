from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils.text import slugify
from decimal import Decimal

def find_model_by_name(model_name):
    """Return the first installed model whose class name matches model_name."""
    for m in apps.get_models():
        if m.__name__.lower() == model_name.lower():
            return m
    return None

def first_existing_field(model, candidates):
    """Return the first field name that exists on the model from a list of candidates."""
    model_fields = {f.name for f in model._meta.get_fields()}
    for c in candidates:
        if c in model_fields:
            return c
    return None

PRODUCT_DATA = [
    {
        "name": "Business Cards — 350gsm, Matt Lamination (Single/Double Sided)",
        "category": "Business Cards",
        "description": (
            "Premium 90×50mm cards on 350gsm board with smooth matt lamination. "
            "Clean edges, crisp colour. Great for first impressions."
        ),
        # Competitive vs Webprinter (50=R290, 100=R300, 200=R320) -> ~10–15% lower.
        "tiers": [
            {"qty": 50,  "price": 255},
            {"qty": 100, "price": 269},
            {"qty": 200, "price": 289},
            {"qty": 500, "price": 499},
        ],
    },
    {
        "name": "A5 Flyers — 130gsm, Full Colour (Single-Sided)",
        "category": "Flyers",
        "description": (
            "Vibrant marketing flyers on 130gsm gloss. Ideal for promos, events, and handouts."
        ),
        # Anchor: Flyerz “A5 double sided from R299” -> make single-sided tiers very competitive.
        "tiers": [
            {"qty": 100,  "price": 259},
            {"qty": 500,  "price": 699},
            {"qty": 1000, "price": 1199},
        ],
    },
    {
        "name": "A4 Flyers — 130gsm, Full Colour (Single-Sided)",
        "category": "Flyers",
        "description": "Bigger canvas for menus, promos and product sheets. Sharp colour on 130gsm.",
        "tiers": [
            {"qty": 100,  "price": 399},
            {"qty": 500,  "price": 999},
            {"qty": 1000, "price": 1699},
        ],
    },
    {
        "name": "Vinyl Stickers — Die-Cut (Gloss/Matt) • Indoor/Outdoor",
        "category": "Stickers",
        "description": (
            "Durable vinyl stickers, any shape. Weather-resistant, perfect for packaging and gear."
        ),
        # Competitive entry points for common sheet-based ordering.
        "tiers": [
            {"qty": 10,   "price": 49},     # ~per A4 sheet (guide)
            {"qty": 50,   "price": 229},
            {"qty": 100,  "price": 399},
            {"qty": 1000, "price": 3490},
        ],
    },
    {
        "name": "A4 Brochures — Tri-Fold (Z-Fold optional) • 150gsm",
        "category": "Brochures",
        "description": "Professional tri-fold brochures on 150gsm. Great for company profiles & menus.",
        "tiers": [
            {"qty": 100,  "price": 699},
            {"qty": 500,  "price": 2299},
            {"qty": 1000, "price": 3799},
        ],
    },
    {
        "name": "A2 Posters — 170gsm, Full Colour",
        "category": "Posters",
        "description": "High-impact A2 posters on sturdy 170gsm. Retail promos, events, notices.",
        "tiers": [
            {"qty": 10,  "price": 399},
            {"qty": 50,  "price": 1499},
            {"qty": 100, "price": 2499},
        ],
    },
    # Add more here if you like: Letterheads, Correx Boards, Roll-Up Banners, etc.
]

CATEGORIES = [
    "Business Cards",
    "Flyers",
    "Stickers",
    "Brochures",
    "Posters",
]

class Command(BaseCommand):
    help = "Seed market-backed product data with competitive SA pricing. Safe on varying models."

    def handle(self, *args, **options):
        # Try to resolve likely model names
        Category = find_model_by_name("Category") or find_model_by_name("ProductCategory")
        Product = find_model_by_name("Product") or find_model_by_name("PrintingProduct")
        PriceTier = find_model_by_name("PriceTier") or find_model_by_name("ProductPrice") or find_model_by_name("VariantPrice")

        if Product is None:
            self.stdout.write(self.style.ERROR(
                "Could not find a Product-like model (tried 'Product', 'PrintingProduct')."
            ))
            return

        # Introspect field names on Product
        price_field = first_existing_field(Product, ["price", "base_price", "unit_price", "starting_price"])
        name_field = first_existing_field(Product, ["name", "title"])
        slug_field = first_existing_field(Product, ["slug"])
        desc_field = first_existing_field(Product, ["description", "desc", "long_description", "summary"])
        active_field = first_existing_field(Product, ["is_active", "active", "enabled"])
        sku_field = first_existing_field(Product, ["sku", "code"])
        # Find any FK to Category
        category_field = None
        if Category:
            for f in Product._meta.get_fields():
                try:
                    if f.is_relation and getattr(f, "remote_field", None) and f.remote_field.model == Category:
                        category_field = f.name
                        break
                except Exception:
                    pass

        created_counts = {"categories": 0, "products": 0, "tiers": 0}

        # Create categories if model exists
        category_objs = {}
        if Category:
            for cname in CATEGORIES:
                defaults = {}
                if slug_field and hasattr(Category, "_meta") and "slug" in {f.name for f in Category._meta.get_fields()}:
                    defaults["slug"] = slugify(cname)
                cat_obj, created = Category.objects.get_or_create(
                    **({"name": cname} if "name" in {f.name for f in Category._meta.get_fields()} else {"title": cname}),
                    defaults=defaults
                )
                category_objs[cname] = cat_obj
                if created:
                    created_counts["categories"] += 1

        # Seed products
        for item in PRODUCT_DATA:
            product_kwargs = {}

            # name/title
            if name_field:
                product_kwargs[name_field] = item["name"]

            # description
            if desc_field:
                product_kwargs[desc_field] = item["description"]

            # slug
            if slug_field:
                product_kwargs[slug_field] = slugify(item["name"])

            # category
            if Category and category_field and item.get("category") in category_objs:
                product_kwargs[category_field] = category_objs[item["category"]]

            # pick a "starting price" (lowest tier) if we have a price field
            if price_field and item["tiers"]:
                product_kwargs[price_field] = Decimal(str(item["tiers"][0]["price"]))

            # SKU
            if sku_field:
                product_kwargs[sku_field] = f"SKU-{slugify(item['name'])[:30]}"

            # upsert by name/title
            lookup = {name_field: item["name"]} if name_field else {}
            obj, created = Product.objects.update_or_create(  # idempotent
                **lookup, defaults=product_kwargs
            )
            if created:
                created_counts["products"] += 1

            # activate if field exists
            if active_field:
                setattr(obj, active_field, True)
                obj.save(update_fields=[active_field])

            # Optional: create price tiers if a model exists with sensible fields
            if PriceTier:
                # Detect likely field names on PriceTier
                pt_product_fk = None
                pt_qty_field = first_existing_field(PriceTier, ["qty", "quantity", "min_qty"])
                pt_price_field = first_existing_field(PriceTier, ["price", "unit_price", "amount"])
                for f in PriceTier._meta.get_fields():
                    try:
                        if f.is_relation and getattr(f, "remote_field", None) and f.remote_field.model == Product:
                            pt_product_fk = f.name
                            break
                    except Exception:
                        pass

                if pt_product_fk and pt_qty_field and pt_price_field:
                    for tier in item["tiers"]:
                        tier_lookup = {
                            pt_product_fk: obj,
                            pt_qty_field: tier["qty"],
                        }
                        defaults = {pt_price_field: Decimal(str(tier["price"]))}
                        _, t_created = PriceTier.objects.update_or_create(**tier_lookup, defaults=defaults)
                        if t_created:
                            created_counts["tiers"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Categories created: {created_counts['categories']}, "
            f"Products created: {created_counts['products']}, "
            f"Price tiers created: {created_counts['tiers']}."
        ))
