import json
from unittest import mock
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from carsshop.models import Order
from carshop_api.views import MonoAcquiringWebhookReceiver


@pytest.mark.django_db
class TestOrderViewSet:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def order_data(self):
        return {
            "order": [
                {"car_type": 1, "quantity": 2},
                {"car_type": 2, "quantity": 1},
            ]
        }

    def test_create_order(self, api_client, order_data):
        url = reverse("orders-list")
        response = api_client.post(
            url, data=json.dumps(order_data), content_type="application/json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "invoice_url" in response.data

        order = Order.objects.first()
        assert order.client == api_client.user
        assert order.car_types.count() == len(order_data["order"])

    # Add more test cases as needed


@pytest.mark.django_db
class TestMonoAcquiringWebhookReceiver:
    @pytest.fixture
    def mock_verify_signature(self, monkeypatch):
        def mock_verify_signature(request):
            return True

        monkeypatch.setattr(
            MonoAcquiringWebhookReceiver, "_verify_signature", mock_verify_signature
        )

    def test_webhook_receiver_success(self, mock_verify_signature, client):
        url = reverse("webhook-mono")
        data = {
            "reference": 1,
            "invoiceId": "123456",
            "status": "error",
        }

        with patch("your_app.views.create_invoice") as mock_create_invoice:
            response = client.post(url, data=data, content_type="application/json")

        assert response.status_code == status.HTTP_200_OK
        assert Order.objects.get(id=1).status == "success"
        mock_create_invoice.assert_called_once_with(Order.objects.get(id=1), mock.ANY)

    def test_webhook_receiver_failure(self, mock_verify_signature, client):
        url = reverse("webhook-mono")
        data = {
            "reference": 1,
            "invoiceId": "123456",
            "status": "error",
        }

        with patch("your_app.views.create_invoice") as mock_create_invoice:
            response = client.post(url, data=data, content_type="application/json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Order.objects.get(id=1).status == "error"
        mock_create_invoice.assert_not_called()
