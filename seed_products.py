from decimal import Decimal
from django.utils.text import slugify
from products.models import Product, QuantityTier, ProductOption, OptionalService

# Clear old products if needed
Product.objects.all().delete()

option_types = {
    "Format": ["Single-Sided", "Double-Sided"],
    "Finish": ["Gloss", "Matte", "None"],
    "Paper": ["Standard", "350gsm Premium"]
}

service_templates = [
    ("3-Day Design Service", 200),
    ("Express Delivery (1-2 days)", 99),
    ("Standard Delivery (3-5 days)", 0)
]

names = [
    "Premium Business Cards",
    "Luxury Flyers",
    "Eco-Friendly Brochures",
    "Professional Letterheads",
    "Matte Postcards"
]

for name in names:
        product = Product.objects.create(
            name=name,
            slug=slugify(name),
            description="High-quality printed product for business use.",
            image="product_images/sample.jpg"
        )

for qty, price in [(100, 375), (250, 675), (500, 1150), (1000, 1850)]:
        QuantityTier.objects.create(
            product=product,
            quantity=qty,
            base_price=Decimal(price)
        )

for opt_type, values in option_types.items():
        for val in values:
            ProductOption.objects.create(
                product=product,
                option_type=opt_type,
                value=val,
                price_modifier=Decimal("15.00") if val != "None" else Decimal("0.00")
            )

for label, price in service_templates:
        OptionalService.objects.create(
            product=product,
            label=label,
            price=Decimal(price)
        )
