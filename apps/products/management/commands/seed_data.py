"""Management command to seed Orderimo with realistic test data."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from apps.products.models import Category, Product

User = get_user_model()


CATEGORIES = [
    ("Electronics", "electronics", "Gadgets, devices, and accessories"),
    ("Clothing", "clothing", "Fashion and apparel"),
    ("Home & Living", "home-living", "Home decor and essentials"),
    ("Sports", "sports", "Fitness and outdoor gear"),
]

PRODUCTS = [
    # Electronics
    ("Gaming Mouse Pro", "gaming-mouse-pro", "ELEC-001", "electronics", "59.99", 25,
     "High-precision optical sensor, customisable RGB, 6 programmable buttons."),
    ("Mechanical Keyboard", "mech-keyboard", "ELEC-002", "electronics", "129.99", 15,
     "Cherry MX Brown switches, full-size layout, USB-C detachable cable."),
    ("USB-C Hub 7-in-1", "usb-c-hub", "ELEC-003", "electronics", "34.99", 40,
     "HDMI 4K, 3x USB-A, SD/microSD, Gigabit Ethernet, 100W PD."),
    ("Webcam HD 1080p", "webcam-hd-1080p", "ELEC-004", "electronics", "49.99", 30,
     "Auto-focus, noise-reducing mic, plug-and-play USB."),
    ("Wireless Earbuds", "wireless-earbuds", "ELEC-005", "electronics", "79.99", 20,
     "ANC, 30hr battery, IPX5 waterproof, multipoint Bluetooth."),
    # Clothing
    ("Cotton T-Shirt", "cotton-tshirt", "CLOTH-001", "clothing", "24.99", 100,
     "100% organic cotton, relaxed fit, available in S/M/L/XL/XXL."),
    ("Denim Jacket", "denim-jacket", "CLOTH-002", "clothing", "79.99", 20,
     "Classic fit, stone-washed denim, brass buttons."),
    ("Running Shorts", "running-shorts", "CLOTH-003", "clothing", "19.99", 60,
     "Lightweight mesh, quick-dry, built-in liner."),
    # Home & Living
    ("Scented Candle", "scented-candle", "HOME-001", "home-living", "18.99", 50,
     "Hand-poured soy wax, 40hr burn time. Vanilla & Sandalwood."),
    ("Desk Lamp", "desk-lamp", "HOME-002", "home-living", "39.99", 20,
     "LED, 3 colour temperatures, touch dimmer, USB charging port."),
    ("Canvas Backpack", "canvas-backpack", "HOME-003", "home-living", "44.99", 30,
     "Water-resistant canvas, padded laptop compartment, 25L."),
    # Sports
    ("Yoga Mat Premium", "yoga-mat", "SPORT-001", "sports", "34.99", 45,
     "6mm thick, non-slip surface, includes carrying strap."),
    ("Resistance Bands Set", "resistance-bands", "SPORT-002", "sports", "14.99", 80,
     "5 resistance levels, includes door anchor and handles."),
    ("Running Watch", "running-watch", "SPORT-003", "sports", "89.99", 12,
     "GPS, heart rate monitor, 7-day battery, waterproof 5ATM."),
]


class Command(BaseCommand):
    help = "Seed the database with realistic test products and a test admin user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Delete all existing products and categories before seeding"
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("Clearing existing data...")
            Product.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            EmailAddress.objects.all().delete()

        # Create superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@orderimo.local",
                password="AdminPass123!"
            )
            self.stdout.write(self.style.SUCCESS("  Created admin user: admin / AdminPass123!"))
        else:
            self.stdout.write("  Admin user already exists")

        # Create categories
        cat_map = {}
        for name, slug, desc in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": desc}
            )
            cat_map[slug] = cat
            status = "Created" if created else "Exists"
            self.stdout.write(f"  {status}: {name}")

        # Create products
        created_count = 0
        for name, slug, sku, cat_slug, price, stock, desc in PRODUCTS:
            p, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": cat_map[cat_slug],
                    "sku": sku,
                    "name": name,
                    "description": desc,
                    "price": price,
                    "stock": stock,
                    "status": Product.Status.ACTIVE,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nSeeded: {len(CATEGORIES)} categories, {created_count} products"
        ))
        self.stdout.write(
            self.style.SUCCESS(
                f"\nTest login: admin / AdminPass123! at http://localhost:8888/admin/"
            )
        )
