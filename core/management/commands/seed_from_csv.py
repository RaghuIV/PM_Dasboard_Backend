from django.core.management.base import BaseCommand
from core.models import Driver, Route, Order
import csv

class Command(BaseCommand):
    help = "Seed DB from CSV files."

    def add_arguments(self, parser):
        parser.add_argument("--drivers", default="core/data/drivers.csv")
        parser.add_argument("--routes", default="core/data/routes.csv")
        parser.add_argument("--orders", default="core/data/orders.csv")

    def handle(self, *args, **opts):
        Driver.objects.all().delete()
        Route.objects.all().delete()
        Order.objects.all().delete()

        # Load Drivers
        with open(opts["drivers"], newline="") as f:
            for row in csv.DictReader(f):
                week = [int(x) for x in row["past_week_hours"].split("|")]
                Driver.objects.create(
                    name=row["name"].strip(),
                    shift_hours=int(row["shift_hours"]),
                    past_week_hours=week,
                )

        # Load Routes
        with open(opts["routes"], newline="") as f:
            for row in csv.DictReader(f):
                Route.objects.create(
                    route_id=int(row["route_id"]),
                    distance_km=float(row["distance_km"]),
                    traffic_level=row["traffic_level"],
                    base_time_min=int(row["base_time_min"]),
                )

        # Load Orders
        def hhmm_to_min(hhmm: str) -> int:
            h, m = hhmm.split(":")
            return int(h) * 60 + int(m)

        with open(opts["orders"], newline="") as f:
            for row in csv.DictReader(f):
                Order.objects.create(
                    order_id=int(row["order_id"]),
                    value_rs=int(row["value_rs"]),
                    route=Route.objects.get(route_id=int(row["route_id"])),
                    delivery_time_min=hhmm_to_min(row["delivery_time"]),
                )

        self.stdout.write(self.style.SUCCESS("Seeded drivers, routes, orders successfully."))
