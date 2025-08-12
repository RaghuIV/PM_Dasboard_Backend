from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Driver(models.Model):
    name = models.CharField(max_length=100, unique=True)
    shift_hours = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    past_week_hours = models.JSONField(default=list)  

    def is_fatigued_today(self) -> bool:
        if not self.past_week_hours: return False
        return int(self.past_week_hours[-1]) > 8

    def __str__(self): return self.name

class Route(models.Model):
    route_id = models.PositiveIntegerField(unique=True)
    distance_km = models.FloatField(validators=[MinValueValidator(0)])
    traffic_level = models.CharField(max_length=10, choices=[("Low","Low"),("Medium","Medium"),("High","High")])
    base_time_min = models.PositiveIntegerField()

    def __str__(self): return f"Route {self.route_id}"

class Order(models.Model):
    order_id = models.PositiveIntegerField(unique=True)
    value_rs = models.PositiveIntegerField()
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="orders")
    delivery_time_min = models.PositiveIntegerField(help_text="Planned delivery time in minutes")

    def __str__(self): return f"Order {self.order_id}"

class SimulationResult(models.Model):
    ran_at = models.DateTimeField(default=timezone.now)
    inputs = models.JSONField()
    kpis = models.JSONField()
    totals = models.JSONField(default=dict)

class DeliveryAssignment(models.Model):
    simulation = models.ForeignKey(SimulationResult, on_delete=models.CASCADE, related_name="assignments")
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    planned_start = models.DateTimeField()
    planned_duration_min = models.PositiveIntegerField()
    on_time = models.BooleanField()
    penalty_rs = models.IntegerField(default=0)
    bonus_rs = models.IntegerField(default=0)
    fuel_cost_rs = models.IntegerField(default=0)
    profit_rs = models.IntegerField(default=0)
