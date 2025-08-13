from django.db import migrations
from pathlib import Path
import csv

def hhmm_to_min(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def seed_initial(apps, schema_editor):
    Driver = apps.get_model("core", "Driver")
    Route = apps.get_model("core", "Route")
    Order  = apps.get_model("core", "Order")

    # Skip if any data already exists (prod-safe)
    if Driver.objects.exists() or Route.objects.exists() or Order.objects.exists():
        return

    base = (Path(__file__).resolve().parent.parent / "data")
    drivers_csv = base / "drivers.csv"
    routes_csv  = base / "routes.csv"
    orders_csv  = base / "orders.csv"

    # Routes
    with routes_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            Route.objects.create(
                route_id=int(row["route_id"]),
                distance_km=float(row["distance_km"]),
                traffic_level=row["traffic_level"],
                base_time_min=int(row["base_time_min"]),
            )

    # Drivers
    with drivers_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            week = [int(x) for x in row.get("past_week_hours","").split("|")] if row.get("past_week_hours") else []
            Driver.objects.create(
                name=row["name"].strip(),
                shift_hours=int(row["shift_hours"]),
                past_week_hours=week,
            )

    # Orders
    with orders_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            route = Route.objects.get(route_id=int(row["route_id"]))
            Order.objects.create(
                order_id=int(row["order_id"]),
                value_rs=int(row["value_rs"]),
                route=route,
                delivery_time_min=hhmm_to_min(row["delivery_time"]),
            )

class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(seed_initial, reverse_code=migrations.RunPython.noop)]
