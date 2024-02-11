from django.urls import path
from . import views

urlpatterns = [
    path("", views.car_list, name="car_list"),
    path("create-cartype/", views.create_car_type, name="create_cartype"),
    path("create-dealership/", views.create_dealership, name="create_dealership"),
    path("create-car/", views.create_car, name="create_car"),
    path("create-client/", views.create_client, name="create_client"),
    path("payment/", views.payment, name="payment"),
    path("payment_success/<order_id>", views.payment_success, name="payment_success"),
]
