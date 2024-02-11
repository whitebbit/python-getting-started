from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from carshop_api.invoices import create_invoice
from .forms import DealershipForm, CarTypeForm, CarForm, ClientForm
from .models import CarType, Order, Dealership


def car_list(request):
    dealerships = Dealership.objects.all()
    dealership_cars_data = {}

    for dealership in dealerships:
        dealership_cars_data[dealership] = list(dealership.available_car_types.all())

    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return redirect("accounts/signup/")

        car_type_id = request.POST.get("car_type_id")
        quantity = int(request.POST.get("quantity"))
        car_type = CarType.objects.get(id=car_type_id)

        order, created_order = Order.objects.get_or_create(client=user, is_paid=False)

        order.add_car_type_to_order(car_type, quantity)

        request.session["order_id"] = order.id
        return redirect("car_list")

    return render(
        request,
        "car_type_list.html",
        {
            "dealership_cars_data": dealership_cars_data,
            "order_id": request.session.get("order_id", 0),
        },
    )


def create_car_type(request):
    if request.method == "POST":
        form = CarTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_cartype")
    else:
        form = CarTypeForm()

    return render(request, "create_car_type.html", {"form": form})


def create_dealership(request):
    if request.method == "POST":
        form = DealershipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_dealership")
    else:
        form = DealershipForm()

    return render(request, "create_dealership.html", {"form": form})


def create_car(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_car")
    else:
        form = CarForm()

    return render(request, "create_car.html", {"form": form})


def create_client(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("create_client")
    else:
        form = ClientForm()

    return render(request, "create_client.html", {"form": form})


def payment(request):
    if request.user.id is None:
        return render(request, "payment_error.html")

    request.session.clear()
    order = Order.objects.filter(client_id=request.user.id, is_paid=False).first()
    if order is not None:
        if request.method == "POST":
            order.complete_order()
            request.session["order_id"] = 0
            create_invoice(
                order, reverse("payment_success", kwargs={"order_id": order.id})
            )
            return redirect(order.invoice_url)
    else:
        return render(request, "payment_error.html")

    return render(
        request,
        "payment.html",
        {"order": order, "order_quantities": order.car_types.all()},
    )


def payment_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "payment_success.html", {"order": order})
