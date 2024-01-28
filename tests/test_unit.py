import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest
from carsshop.models import Order, OrderQuantity, CarType


@pytest.mark.django_db
def test_order_view_set(user):
    car_type = CarType.objects.create(name="TestCar", brand="TestBrand", price=100)
    client = APIClient()

    payload = {
        "order": [{"car_type": car_type.id, "quantity": 2}]
    }

    client.force_authenticate(user=user)

    response = client.post(reverse("orders-list"), data=json.dumps(payload), content_type="application/json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "invoice_url" in response.data

    order = Order.objects.first()
    assert order is not None
    assert order.client == user
    assert order.car_types.count() == 1

    client.force_authenticate(user=None)


@pytest.mark.django_db
def test_mono_acquiring_webhook_receiver(client, order):
    payload = {
        "reference": order.id,
        "invoiceId": order.order_id,
        "status": "success"
    }

    response = client.post(reverse("webhook-mono"), data=json.dumps(payload), content_type="application/json")

    assert response.status_code == status.HTTP_200_OK
    assert "status" in response.data and response.data["status"] == "ok"

    order.refresh_from_db()
    assert order.status == "success"
