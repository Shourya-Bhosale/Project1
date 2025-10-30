from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = 'Set price of 250ml Gir Cow Ghee to Rs 10'

    def handle(self, *args, **options):
        updated = 0
        try:
            qs = Product.objects.filter(size_ml=250)
            for p in qs:
                old = p.price
                p.price = 10
                p.save(update_fields=['price'])
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Updated {p.name} from Rs {old} to Rs 10"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error updating price: {e}"))
        if updated == 0:
            self.stdout.write(self.style.WARNING("No 250ml product found to update"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. Updated {updated} product(s)."))


