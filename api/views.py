from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.models import Driver, Route, Order, SimulationResult, DeliveryAssignment
from .serializers import (DriverSerializer, RouteSerializer, OrderSerializer,
                          SimulationResultSerializer)
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated


class DriverViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Driver.objects.all().order_by("id")
    serializer_class = DriverSerializer

class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Route.objects.all().order_by("route_id")
    serializer_class = RouteSerializer

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.select_related("route").all().order_by("order_id")
    serializer_class = OrderSerializer

class SimulationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = SimulationResult.objects.order_by("-ran_at")
    serializer_class = SimulationResultSerializer

    @action(detail=False, methods=["post"])
    def run(self, request):
        try:
            available_drivers = int(request.data.get("available_drivers"))
            route_start_time = request.data.get("route_start_time", "09:00")
            max_hours_per_driver = int(request.data.get("max_hours_per_driver"))
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid parameter types."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if available_drivers <= 0 or max_hours_per_driver <= 0:
            return Response(
                {"error": "available_drivers and max_hours_per_driver must be positive."},
                status=status.HTTP_400_BAD_REQUEST
            )
             
        total_drivers_count = Driver.objects.count()

        if available_drivers > total_drivers_count:
          return Response(
        {
            "error": "available_drivers exceeds total drivers in database",
            "requested": available_drivers,
            "available_in_db": total_drivers_count
        },
        status=status.HTTP_400_BAD_REQUEST
        )

        drivers = list(Driver.objects.all().order_by("id")[:available_drivers])
        if not drivers:
            return Response({"error": "No drivers available."}, status=400)

        try:
            start_hour, start_minute = map(int, route_start_time.split(":"))
        except ValueError:
            return Response({"error": "route_start_time must be HH:MM format"}, status=400)

        now = timezone.now().replace(
            hour=start_hour, minute=start_minute, second=0, microsecond=0
        )

        
        driver_minutes_used = {d.id: 0 for d in drivers}
        on_time_count = 0
        late_count = 0
        total_profit = 0
        fuel_by_traffic = {"Low": 0, "Medium": 0, "High": 0}

        sim_result = SimulationResult.objects.create(
            ran_at=timezone.now(),
            inputs={
                "available_drivers": available_drivers,
                "route_start_time": route_start_time,
                "max_hours_per_driver": max_hours_per_driver
            },
            kpis={}, totals={}
        )

        
        orders = list(Order.objects.select_related("route").all().order_by("order_id"))
        driver_idx = 0

        for order in orders:
            
            spins = 0
            chosen_driver = None
            while spins < len(drivers):
                candidate = drivers[driver_idx % len(drivers)]
                if driver_minutes_used[candidate.id] < max_hours_per_driver * 60:
                    chosen_driver = candidate
                    break
                driver_idx += 1
                spins += 1

            if not chosen_driver:
                break  

            route = order.route
            fatigue_factor = 1.3 if chosen_driver.is_fatigued_today() else 1.0
            actual_time = int(round(route.base_time_min * fatigue_factor))

            # Company Rule 1: Late Delivery Penalty
            late_threshold = route.base_time_min + 10
            on_time = actual_time <= late_threshold
            penalty = 0 if on_time else 50

            # Company Rule 4: Fuel Cost
            fuel_cost = route.distance_km * 5
            if route.traffic_level == "High":
                fuel_cost += route.distance_km * 2
            fuel_cost = int(round(fuel_cost))
            fuel_by_traffic[route.traffic_level] += fuel_cost

            # Company Rule 3: High-Value Bonus
            bonus = 0
            if order.value_rs > 1000 and on_time:
                bonus = int(round(order.value_rs * 0.10))

            # Company Rule 5: Profit
            profit = order.value_rs + bonus - penalty - fuel_cost

            # Update counters
            if on_time:
                on_time_count += 1
            else:
                late_count += 1
            total_profit += profit

            # Save assignment
            DeliveryAssignment.objects.create(
                simulation=sim_result,
                order=order,
                driver=chosen_driver,
                planned_start=now + timedelta(minutes=driver_minutes_used[chosen_driver.id]),
                planned_duration_min=actual_time,
                on_time=on_time,
                penalty_rs=penalty,
                bonus_rs=bonus,
                fuel_cost_rs=fuel_cost,
                profit_rs=profit
            )

            # Increment driver time
            driver_minutes_used[chosen_driver.id] += actual_time
            driver_idx += 1

        # Company Rule 6: Efficiency
        total_deliveries = on_time_count + late_count
        efficiency = (on_time_count / total_deliveries * 100) if total_deliveries else 0

        # Save KPIs
        sim_result.kpis = {
            "total_profit": total_profit,
            "efficiency": round(efficiency, 2),
            "on_time": on_time_count,
            "late": late_count
        }
        sim_result.totals = {
            "fuel_by_traffic": fuel_by_traffic
        }
        sim_result.save()

        return Response(SimulationResultSerializer(sim_result).data, status=200)
