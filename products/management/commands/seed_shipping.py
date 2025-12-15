from django.core.management.base import BaseCommand
from products.models import ShippingMethod
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with initial shipping methods'

    def handle(self, *args, **options):
        methods = [
            {"name": "Standard Shipping", "slug": "standard", "price": Decimal("60.00")},
            {"name": "Express Shipping", "slug": "express", "price": Decimal("120.00")},
            {"name": "Pickup", "slug": "pickup", "price": Decimal("0.00")},
        ]

        for method in methods:
            obj, created = ShippingMethod.objects.get_or_create(
                slug=method["slug"],
                defaults={"name": method["name"], "price": method["price"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created shipping method: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Shipping method already exists: {obj.name}"))
