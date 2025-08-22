from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = 'Update existing products with local image paths'

    def handle(self, *args, **options):
        # Update 1L product
        try:
            product_1l = Product.objects.filter(name__icontains='1L').first()
            if product_1l:
                product_1l.image_url = '/static/store/images/product_1l.jpg'
                product_1l.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {product_1l.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating 1L: {e}'))

        # Update 500ml product
        try:
            product_500ml = Product.objects.filter(name__icontains='500ml').first()
            if product_500ml:
                product_500ml.image_url = '/static/store/images/product_500ml.jpg'
                product_500ml.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {product_500ml.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating 500ml: {e}'))

        # Update 250ml product
        try:
            product_250ml = Product.objects.filter(name__icontains='250ml').first()
            if product_250ml:
                product_250ml.image_url = '/static/store/images/product_250ml.jpg'
                product_250ml.save()
                self.stdout.write(self.style.SUCCESS(f'Updated {product_250ml.name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating 250ml: {e}'))

        self.stdout.write(self.style.SUCCESS('Image update completed!'))
