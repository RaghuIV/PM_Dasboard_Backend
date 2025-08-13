from django.test import TestCase
from core.models import Driver, Route, Order
from rest_framework.test import APIClient

class RuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.d = Driver.objects.create(name="Amit", shift_hours=6, past_week_hours=[6,8,7,7,7,6,10]) 
        self.r_high = Route.objects.create(route_id=1, distance_km=10, traffic_level="High", base_time_min=60)
        self.r_low = Route.objects.create(route_id=2, distance_km=10, traffic_level="Low", base_time_min=60)
        Order.objects.create(order_id=1, value_rs=2000, route=self.r_low, delivery_time_min=35)
        Order.objects.create(order_id=2, value_rs=800, route=self.r_high, delivery_time_min=80)

    def run_sim(self):
        return self.client.post("/api/simulations/run/", {
            "available_drivers": 1,
            "route_start_time": "09:00",
            "max_hours_per_driver": 8
        }, format="json")

    def test_fatigue_applies(self):
        res = self.run_sim().json()
        self.assertGreaterEqual(res["kpis"]["late"], 1)

    def test_high_value_bonus_only_on_time(self):
        res = self.run_sim().json()
        self.assertIn("total_profit", res["kpis"])

    def test_fuel_cost_high_vs_low(self):
        res = self.run_sim().json()
        fuel = res["totals"]["fuel_by_traffic"]
        self.assertTrue(fuel["High"] >= 10*7)  
        self.assertTrue(fuel["Low"] >= 10*5)

    def test_late_penalty(self):
        res = self.run_sim().json()
        self.assertGreaterEqual(res["kpis"]["late"], 1)

    def test_efficiency_formula(self):
        res = self.run_sim().json()
        k = res["kpis"]
        total = k["on_time"] + k["late"]
        expected = round((k["on_time"]/total)*100,2) if total else 0.0
        self.assertEqual(k["efficiency"], expected)
