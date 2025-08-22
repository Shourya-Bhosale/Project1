from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def seed_products(sender, **kwargs):
    try:
        from .models import Product
        if Product.objects.count() == 0:
            Product.objects.bulk_create(
                [
                    Product(
                        name='Gir Cow Ghee 1L',
                        size_ml=1000,
                        price=1199,
                        description='Pure A2 Gir Cow Bilona Ghee (1L).',
                        image_url='/static/store/images/product_1l.jpg',
                    ),
                    Product(
                        name='Gir Cow Ghee 500ml',
                        size_ml=500,
                        price=649,
                        description='Pure A2 Gir Cow Bilona Ghee (500ml).',
                        image_url='/static/store/images/product_500ml.jpg',
                    ),
                    Product(
                        name='Gir Cow Ghee 250ml',
                        size_ml=250,
                        price=349,
                        description='Pure A2 Gir Cow Bilona Ghee (250ml).',
                        image_url='/static/store/images/product_250ml.jpg',
                    ),
                ]
            )
    except Exception:
        pass


