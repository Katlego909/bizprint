from decimal import Decimal
from django.utils.text import slugify
from products.models import Product, QuantityTier, ProductOption, OptionalService

# Clear old products if needed
Product.objects.all().delete()


# --- Business Cards ---
bc1 = Product.objects.create(
    name="Premium Business Cards",
    slug=slugify("Premium Business Cards"),
    description="Premium 350gsm business cards with a choice of gloss or matte finish. Perfect for first impressions.",
    image="product_images/business_cards.jpg"
)
for qty, price in [(100, 299), (250, 499), (500, 899), (1000, 1499)]:
    QuantityTier.objects.create(product=bc1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=bc1, option_type="Format", value="Single-Sided", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=bc1, option_type="Format", value="Double-Sided", price_modifier=Decimal("50.00"))
ProductOption.objects.create(product=bc1, option_type="Finish", value="Gloss", price_modifier=Decimal("20.00"))
ProductOption.objects.create(product=bc1, option_type="Finish", value="Matte", price_modifier=Decimal("20.00"))
ProductOption.objects.create(product=bc1, option_type="Paper", value="350gsm Premium", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=bc1, label="3-Day Design Service", price=Decimal(200))
OptionalService.objects.create(product=bc1, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=bc1, label="Standard Delivery (3-5 days)", price=Decimal(0))

bc2 = Product.objects.create(
    name="Eco Kraft Business Cards",
    slug=slugify("Eco Kraft Business Cards"),
    description="Eco-friendly kraft business cards printed on 300gsm recycled board. A natural look for sustainable brands.",
    image="product_images/business_cards_kraft.jpg"
)
for qty, price in [(100, 329), (250, 529), (500, 949), (1000, 1599)]:
    QuantityTier.objects.create(product=bc2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=bc2, option_type="Format", value="Single-Sided", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=bc2, option_type="Format", value="Double-Sided", price_modifier=Decimal("40.00"))
ProductOption.objects.create(product=bc2, option_type="Paper", value="300gsm Kraft", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=bc2, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=bc2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Flyers ---
flyer1 = Product.objects.create(
    name="A5 Full Colour Flyers",
    slug=slugify("A5 Full Colour Flyers"),
    description="Vibrant A5 flyers printed on 130gsm gloss paper. Ideal for promotions and events.",
    image="product_images/flyers.jpg"
)
for qty, price in [(500, 399), (1000, 699), (2500, 1499), (5000, 2499)]:
    QuantityTier.objects.create(product=flyer1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=flyer1, option_type="Size", value="A5", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=flyer1, option_type="Size", value="A4", price_modifier=Decimal("150.00"))
ProductOption.objects.create(product=flyer1, option_type="Paper", value="130gsm Gloss", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=flyer1, option_type="Paper", value="170gsm Matte", price_modifier=Decimal("50.00"))
OptionalService.objects.create(product=flyer1, label="Express Delivery (1-2 days)", price=Decimal(149))
OptionalService.objects.create(product=flyer1, label="Standard Delivery (3-5 days)", price=Decimal(0))

flyer2 = Product.objects.create(
    name="DL Promotional Flyers",
    slug=slugify("DL Promotional Flyers"),
    description="DL size flyers (99x210mm) printed on 150gsm silk paper. Great for inserts and handouts.",
    image="product_images/flyers_dl.jpg"
)
for qty, price in [(500, 349), (1000, 599), (2500, 1299), (5000, 2199)]:
    QuantityTier.objects.create(product=flyer2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=flyer2, option_type="Size", value="DL", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=flyer2, option_type="Paper", value="150gsm Silk", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=flyer2, label="Express Delivery (1-2 days)", price=Decimal(149))
OptionalService.objects.create(product=flyer2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Brochures ---
bro1 = Product.objects.create(
    name="A4 Tri-Fold Brochures",
    slug=slugify("A4 Tri-Fold Brochures"),
    description="A4 brochures folded to DL, printed on 170gsm gloss. Perfect for menus and company profiles.",
    image="product_images/brochures_trifold.jpg"
)
for qty, price in [(250, 799), (500, 1399), (1000, 2499)]:
    QuantityTier.objects.create(product=bro1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=bro1, option_type="Fold", value="Tri-Fold", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=bro1, option_type="Paper", value="170gsm Gloss", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=bro1, label="Express Delivery (1-2 days)", price=Decimal(199))
OptionalService.objects.create(product=bro1, label="Standard Delivery (3-5 days)", price=Decimal(0))

bro2 = Product.objects.create(
    name="A5 Half-Fold Brochures",
    slug=slugify("A5 Half-Fold Brochures"),
    description="A5 brochures folded to A6, printed on 150gsm matte. Ideal for event programs and mini-menus.",
    image="product_images/brochures_halffold.jpg"
)
for qty, price in [(250, 599), (500, 1099), (1000, 1999)]:
    QuantityTier.objects.create(product=bro2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=bro2, option_type="Fold", value="Half-Fold", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=bro2, option_type="Paper", value="150gsm Matte", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=bro2, label="Express Delivery (1-2 days)", price=Decimal(199))
OptionalService.objects.create(product=bro2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Posters ---
post1 = Product.objects.create(
    name="A2 Full Colour Posters",
    slug=slugify("A2 Full Colour Posters"),
    description="A2 posters printed on 200gsm satin paper. Eye-catching for events and promotions.",
    image="product_images/posters_a2.jpg"
)
for qty, price in [(10, 299), (25, 599), (50, 999)]:
    QuantityTier.objects.create(product=post1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=post1, option_type="Size", value="A2", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=post1, option_type="Paper", value="200gsm Satin", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=post1, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=post1, label="Standard Delivery (3-5 days)", price=Decimal(0))

post2 = Product.objects.create(
    name="A1 Promotional Posters",
    slug=slugify("A1 Promotional Posters"),
    description="Large A1 posters printed on 170gsm gloss. Great for retail and advertising.",
    image="product_images/posters_a1.jpg"
)
for qty, price in [(5, 249), (10, 449), (25, 849)]:
    QuantityTier.objects.create(product=post2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=post2, option_type="Size", value="A1", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=post2, option_type="Paper", value="170gsm Gloss", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=post2, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=post2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Stickers ---
stick1 = Product.objects.create(
    name="Round Vinyl Stickers",
    slug=slugify("Round Vinyl Stickers"),
    description="Durable round vinyl stickers, 50mm diameter, waterproof and perfect for branding.",
    image="product_images/stickers_round.jpg"
)
for qty, price in [(100, 199), (250, 399), (500, 699)]:
    QuantityTier.objects.create(product=stick1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=stick1, option_type="Shape", value="Round", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=stick1, option_type="Material", value="Vinyl", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=stick1, label="Express Delivery (1-2 days)", price=Decimal(49))
OptionalService.objects.create(product=stick1, label="Standard Delivery (3-5 days)", price=Decimal(0))

stick2 = Product.objects.create(
    name="Square Paper Stickers",
    slug=slugify("Square Paper Stickers"),
    description="Square stickers, 50x50mm, printed on gloss paper. Affordable for packaging and gifts.",
    image="product_images/stickers_square.jpg"
)
for qty, price in [(100, 149), (250, 299), (500, 549)]:
    QuantityTier.objects.create(product=stick2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=stick2, option_type="Shape", value="Square", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=stick2, option_type="Material", value="Gloss Paper", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=stick2, label="Express Delivery (1-2 days)", price=Decimal(49))
OptionalService.objects.create(product=stick2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- T-shirts ---
ts1 = Product.objects.create(
    name="Classic White T-shirt",
    slug=slugify("Classic White T-shirt"),
    description="100% cotton white t-shirt with custom full-colour print. Unisex fit.",
    image="product_images/tshirt_white.jpg"
)
for qty, price in [(10, 799), (25, 1799), (50, 3299)]:
    QuantityTier.objects.create(product=ts1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=ts1, option_type="Size", value="S", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=ts1, option_type="Size", value="M", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=ts1, option_type="Size", value="L", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=ts1, option_type="Size", value="XL", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=ts1, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=ts1, label="Standard Delivery (3-5 days)", price=Decimal(0))

ts2 = Product.objects.create(
    name="Premium Black T-shirt",
    slug=slugify("Premium Black T-shirt"),
    description="Premium black t-shirt, 180gsm, with custom logo print. Soft and durable.",
    image="product_images/tshirt_black.jpg"
)
for qty, price in [(10, 899), (25, 1999), (50, 3599)]:
    QuantityTier.objects.create(product=ts2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=ts2, option_type="Size", value="S", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=ts2, option_type="Size", value="M", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=ts2, option_type="Size", value="L", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=ts2, option_type="Size", value="XL", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=ts2, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=ts2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Uniforms ---
uni1 = Product.objects.create(
    name="Classic Work Shirt",
    slug=slugify("Classic Work Shirt"),
    description="Poly-cotton work shirt, available in navy or khaki. Embroidery option available.",
    image="product_images/uniforms_shirt.jpg"
)
for qty, price in [(5, 499), (10, 899), (25, 1999)]:
    QuantityTier.objects.create(product=uni1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=uni1, option_type="Colour", value="Navy", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=uni1, option_type="Colour", value="Khaki", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=uni1, label="Embroidery (per shirt)", price=Decimal(50))
OptionalService.objects.create(product=uni1, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=uni1, label="Standard Delivery (3-5 days)", price=Decimal(0))

uni2 = Product.objects.create(
    name="Chef Jacket",
    slug=slugify("Chef Jacket"),
    description="Professional chef jacket, double-breasted, available in white or black.",
    image="product_images/uniforms_chef.jpg"
)
for qty, price in [(2, 399), (5, 899), (10, 1699)]:
    QuantityTier.objects.create(product=uni2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=uni2, option_type="Colour", value="White", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=uni2, option_type="Colour", value="Black", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=uni2, label="Express Delivery (1-2 days)", price=Decimal(99))
OptionalService.objects.create(product=uni2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Packaging ---
pack1 = Product.objects.create(
    name="Custom Printed Boxes",
    slug=slugify("Custom Printed Boxes"),
    description="Corrugated boxes with full-colour print. Perfect for e-commerce and retail packaging.",
    image="product_images/packaging_boxes.jpg"
)
for qty, price in [(50, 1499), (100, 2599), (250, 5999)]:
    QuantityTier.objects.create(product=pack1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=pack1, option_type="Size", value="Small", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=pack1, option_type="Size", value="Medium", price_modifier=Decimal("200.00"))
ProductOption.objects.create(product=pack1, option_type="Size", value="Large", price_modifier=Decimal("400.00"))
OptionalService.objects.create(product=pack1, label="Express Delivery (1-2 days)", price=Decimal(299))
OptionalService.objects.create(product=pack1, label="Standard Delivery (3-5 days)", price=Decimal(0))

pack2 = Product.objects.create(
    name="Printed Paper Bags",
    slug=slugify("Printed Paper Bags"),
    description="Recyclable paper bags with your logo. Great for retail and events.",
    image="product_images/packaging_bags.jpg"
)
for qty, price in [(100, 799), (250, 1799), (500, 2999)]:
    QuantityTier.objects.create(product=pack2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=pack2, option_type="Size", value="Small", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=pack2, option_type="Size", value="Large", price_modifier=Decimal("150.00"))
OptionalService.objects.create(product=pack2, label="Express Delivery (1-2 days)", price=Decimal(149))
OptionalService.objects.create(product=pack2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Corporate Gifts ---
gift1 = Product.objects.create(
    name="Branded Metal Pens",
    slug=slugify("Branded Metal Pens"),
    description="Metal ballpoint pens with laser engraving. Supplied in a gift box.",
    image="product_images/gifts_pens.jpg"
)
for qty, price in [(50, 499), (100, 899), (250, 1999)]:
    QuantityTier.objects.create(product=gift1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=gift1, option_type="Colour", value="Silver", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=gift1, option_type="Colour", value="Blue", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=gift1, label="Express Delivery (1-2 days)", price=Decimal(49))
OptionalService.objects.create(product=gift1, label="Standard Delivery (3-5 days)", price=Decimal(0))

gift2 = Product.objects.create(
    name="Custom Coffee Mugs",
    slug=slugify("Custom Coffee Mugs"),
    description="Ceramic mugs with full-colour wrap print. Dishwasher safe.",
    image="product_images/gifts_mugs.jpg"
)
for qty, price in [(24, 399), (48, 749), (96, 1399)]:
    QuantityTier.objects.create(product=gift2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=gift2, option_type="Colour", value="White", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=gift2, option_type="Colour", value="Black", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=gift2, label="Express Delivery (1-2 days)", price=Decimal(49))
OptionalService.objects.create(product=gift2, label="Standard Delivery (3-5 days)", price=Decimal(0))

# --- Personalized Gifts ---
pers1 = Product.objects.create(
    name="Photo Keyrings",
    slug=slugify("Photo Keyrings"),
    description="Acrylic keyrings with your custom photo. Great for events and giveaways.",
    image="product_images/personalized_keyrings.jpg"
)
for qty, price in [(20, 199), (50, 399), (100, 749)]:
    QuantityTier.objects.create(product=pers1, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=pers1, option_type="Shape", value="Rectangle", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=pers1, option_type="Shape", value="Heart", price_modifier=Decimal("10.00"))
OptionalService.objects.create(product=pers1, label="Express Delivery (1-2 days)", price=Decimal(49))
OptionalService.objects.create(product=pers1, label="Standard Delivery (3-5 days)", price=Decimal(0))

pers2 = Product.objects.create(
    name="Custom Mouse Pads",
    slug=slugify("Custom Mouse Pads"),
    description="Personalized mouse pads with your image or logo. Non-slip rubber base.",
    image="product_images/personalized_mousepads.jpg"
)
for qty, price in [(10, 249), (25, 499), (50, 899)]:
    QuantityTier.objects.create(product=pers2, quantity=qty, base_price=Decimal(price))
ProductOption.objects.create(product=pers2, option_type="Shape", value="Rectangle", price_modifier=Decimal("0.00"))
ProductOption.objects.create(product=pers2, option_type="Shape", value="Round", price_modifier=Decimal("0.00"))
OptionalService.objects.create(product=pers2, label="Express Delivery (1-2 days)", price=Decimal(49))
OptionalService.objects.create(product=pers2, label="Standard Delivery (3-5 days)", price=Decimal(0))
