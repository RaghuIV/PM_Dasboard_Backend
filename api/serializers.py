from rest_framework import serializers
from core.models import Driver, Route, Order, SimulationResult, DeliveryAssignment

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = "__all__"

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

class DeliveryAssignmentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.order_id", read_only=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)

    class Meta:
        model = DeliveryAssignment
        fields = ["id","order_id","driver_name","planned_start","planned_duration_min",
                  "on_time","penalty_rs","bonus_rs","fuel_cost_rs","profit_rs"]

class SimulationResultSerializer(serializers.ModelSerializer):
    assignments = DeliveryAssignmentSerializer(many=True, read_only=True)
    class Meta:
        model = SimulationResult
        fields = ["id","ran_at","inputs","kpis","totals","assignments"]
