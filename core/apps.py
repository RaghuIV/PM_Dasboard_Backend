# core/apps.py
import os
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command

def seed_if_empty(sender, **kwargs):
    # Avoid running during tests unless you want that
    import sys
    if "pytest" in sys.modules or "test" in sys.argv:
        return

    from core.models import Driver, Route, Order

    # If any data exists, do nothing
    if Driver.objects.exists() or Route.objects.exists() or Order.objects.exists():
        return

    # Optional: only auto-seed when explicitly enabled (e.g., in dev)
    if os.environ.get("AUTO_SEED") != "1":
        return

    # Run your existing management command
    # (replace 'seed_db' with your command name)
    call_command("seed_db")
    # or with custom CSVs:
    # call_command("seed_db", drivers="core/data/drivers.csv", routes="core/data/routes.csv", orders="core/data/orders.csv")

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Connect after this app’s migrations run
        post_migrate.connect(seed_if_empty, sender=self)
