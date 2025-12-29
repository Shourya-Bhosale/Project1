# Django imports
from django.apps import AppConfig


class StoreConfig(AppConfig):
    """Store app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        """Connect signals when app is ready."""
        try:
            import store.signals  # noqa: F401
        except Exception:
            pass


