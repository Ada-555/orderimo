"""Dashboard views — store overview for superusers."""

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order
from apps.products.models import Product
from apps.accounts.models import User


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
def dashboard(request):
    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    total_revenue = Order.objects.filter(
        status__in=["confirmed", "processing", "shipped", "delivered"]
    ).aggregate(total=Sum("grand_total"))["total"] or 0

    orders_30d = Order.objects.filter(created_at__gte=last_30_days).count()
    products_count = Product.objects.count()
    users_count = User.objects.count()

    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:10]

    orders_by_status = (
        Order.objects
        .values("status")
        .annotate(count=Count("id"))
    )

    context = {
        "total_revenue": total_revenue,
        "orders_30d": orders_30d,
        "products_count": products_count,
        "users_count": users_count,
        "recent_orders": recent_orders,
        "orders_by_status": orders_by_status,
    }
    return render(request, "dashboard/index.html", context)
