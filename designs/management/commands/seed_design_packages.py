from django.core.management.base import BaseCommand
from designs.models import DesignPackage
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with initial design packages'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding design packages...')

        packages = [
            {
                "title": "Logo Design - Basic",
                "description": "3 Concepts, 2 Revisions. Final files in JPG and PNG.",
                "price": Decimal("450.00")
            },
            {
                "title": "Logo Design - Premium",
                "description": "5 Concepts, Unlimited Revisions. Source files (AI, EPS, PDF) included.",
                "price": Decimal("1200.00")
            },
            {
                "title": "Business Card Design",
                "description": "Double-sided business card design. Print-ready PDF.",
                "price": Decimal("350.00")
            },
            {
                "title": "Flyer / Poster Design",
                "description": "A5 or A4 flyer design. Single sided.",
                "price": Decimal("550.00")
            },
            {
                "title": "Social Media Kit",
                "description": "Profile pictures and banners for Facebook, Instagram, and LinkedIn.",
                "price": Decimal("850.00")
            },
            {
                "title": "Company Profile",
                "description": "Up to 8 pages. Professional layout and typesetting.",
                "price": Decimal("2500.00")
            }
        ]

        for pkg_data in packages:
            package, created = DesignPackage.objects.get_or_create(
                title=pkg_data['title'],
                defaults={
                    'description': pkg_data['description'],
                    'price': pkg_data['price']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created package: {package.title}"))
            else:
                self.stdout.write(f"Package already exists: {package.title}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded design packages.'))
