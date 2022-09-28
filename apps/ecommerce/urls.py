from django.urls import path
from apps.ecommerce.views import (
    ProductsView,
    purchase,
    stripe_config,
    create_checkout_session,
    success,
    cancelled,
    stripe_webhook
)

urlpatterns = [
    path("products/", ProductsView.as_view()),
    path("purchase/", purchase),
    path("config/", stripe_config),
    path("create-checkout-session/", create_checkout_session),
    path("success/", success, name="stripe-success"),
    path("cancelled/", cancelled, name="stripe-cancelled"),
    path('webhook/', stripe_webhook)

]
