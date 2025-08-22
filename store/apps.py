from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Connect signals (e.g., product seeding after migrations)
        try:
            import store.signals  # noqa: F401
        except Exception:
            pass


