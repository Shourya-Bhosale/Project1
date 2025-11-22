from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = 'Update all product prices to match home screen: 250ml=549, 500ml=1035, 1L=1999'

    def handle(self, *args, **options):
        price_map = {
            250: 549,
            500: 1035,
            1000: 1999
        }
        
        updated = 0
        for size_ml, price in price_map.items():
            try:
                qs = Product.objects.filter(size_ml=size_ml, is_active=True)
                for p in qs:
                    old = p.price
                    if old != price:
                        p.price = price
                        p.save(update_fields=['price'])
                        updated += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Updated {p.name} ({size_ml}ml) from Rs {old} to Rs {price}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{p.name} ({size_ml}ml) already has correct price Rs {price}"
                            )
                        )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error updating {size_ml}ml products: {e}")
                )
        
        if updated == 0:
            self.stdout.write(self.style.WARNING("No products needed price updates"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Done. Updated {updated} product(s).")
            )

