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
                "description": (
                    "Perfect for startups and small businesses.\n"
                    "- 2 logo concepts\n"
                    "- 2 rounds of revisions\n"
                    "- Final files: JPG, PNG"
                ),
                "price": Decimal("1200.00")
            },
            {
                "title": "Logo Design - Premium",
                "description": (
                    "For established brands needing a professional look.\n"
                    "- 4 logo concepts\n"
                    "- Unlimited revisions\n"
                    "- All source files: AI, EPS, PDF, PNG, JPG\n"
                    "- Basic brand guide included"
                ),
                "price": Decimal("2800.00")
            },
            {
                "title": "Business Card Design",
                "description": (
                    "Custom double-sided business card design.\n"
                    "- Print-ready PDF and source file\n"
                    "- 1 revision included"
                ),
                "price": Decimal("350.00")
            },
            {
                "title": "Flyer / Poster Design",
                "description": (
                    "A5, A4, or DL flyer/poster design.\n"
                    "- 2 concepts\n"
                    "- 1 revision\n"
                    "- Print and web-ready files"
                ),
                "price": Decimal("550.00")
            },
            {
                "title": "Social Media Kit",
                "description": (
                    "Profile and cover images for all major platforms.\n"
                    "- Facebook, Instagram, LinkedIn, Twitter\n"
                    "- 3 post templates\n"
                    "- Includes PNG and PSD files"
                ),
                "price": Decimal("850.00")
            },
            {
                "title": "Company Profile (8 pages)",
                "description": (
                    "Up to 8 pages. Professional layout, typesetting, and imagery.\n"
                    "- Print and digital PDF"
                ),
                "price": Decimal("2500.00")
            },
            {
                "title": "Company Profile (16 pages)",
                "description": (
                    "Up to 16 pages. Custom design, typesetting, and imagery.\n"
                    "- Print and digital PDF"
                ),
                "price": Decimal("4200.00")
            },
            {
                "title": "Brand Identity Kit",
                "description": (
                    "Complete brand identity solution.\n"
                    "- Logo\n"
                    "- Business card\n"
                    "- Letterhead\n"
                    "- Email signature\n"
                    "- Social media kit\n"
                    "- Brand style guide\n"
                    "- All source files included"
                ),
                "price": Decimal("5200.00")
            },
            {
                "title": "Letterhead Design",
                "description": (
                    "Professional letterhead design.\n"
                    "- Print and Word template included"
                ),
                "price": Decimal("300.00")
            },
            {
                "title": "Email Signature Design",
                "description": (
                    "Custom HTML email signature.\n"
                    "- Compatible with Outlook, Gmail, and Apple Mail"
                ),
                "price": Decimal("250.00")
            },
            {
                "title": "Presentation Template",
                "description": (
                    "Custom PowerPoint or Google Slides template.\n"
                    "- Includes cover, content, and closing slides"
                ),
                "price": Decimal("950.00")
            },
            {
                "title": "Product Catalogue Design",
                "description": (
                    "Up to 12 pages. Product layout, pricing tables, and imagery.\n"
                    "- Print and digital PDF"
                ),
                "price": Decimal("3500.00")
            },
            {
                "title": "Menu Design",
                "description": (
                    "A4 or trifold menu design for restaurants or cafes.\n"
                    "- Print and digital PDF"
                ),
                "price": Decimal("950.00")
            },
            {
                "title": "Event Invitation Design",
                "description": (
                    "Custom invitation for print or digital RSVP.\n"
                    "- 1 revision included"
                ),
                "price": Decimal("400.00")
            },
            {
                "title": "Roll-Up Banner Design",
                "description": (
                    "Design for 850x2000mm pull-up banner.\n"
                    "- Print-ready PDF"
                ),
                "price": Decimal("600.00")
            },
        ]


        for pkg_data in packages:
            package, created = DesignPackage.objects.update_or_create(
                title=pkg_data['title'],
                defaults={
                    'description': pkg_data['description'],
                    'price': pkg_data['price']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created package: {package.title}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated package: {package.title}"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded design packages.'))
