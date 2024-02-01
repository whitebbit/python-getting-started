import base64
import hashlib

import ecdsa
import requests
from django.conf import settings

from carsshop.models import Order

from carshop_api.models import MonoSettings


def get_monobank_public_key():
    r = requests.get(
        "https://api.monobank.ua/api/merchant/pubkey",
        headers={"X-Token": settings.MONOBANK_TOKEN},
    )
    r.raise_for_status()
    return r.json()["key"]


def _verify_signature(x_sign_base64, body: bytes, public_key):
    pub_key_bytes = base64.b64decode(public_key)
    signature_bytes = base64.b64decode(x_sign_base64)
    pub_key = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())
    ok = pub_key.verify(
        signature_bytes,
        body,
        sigdecode=ecdsa.util.sigdecode_der,
        hashfunc=hashlib.sha256,
    )
    return ok


def verify_signature(request):
    ok = _verify_signature(
        request.headers["X-Sign"],
        request.body,
        MonoSettings.get_latest_or_add(get_monobank_public_key).public_key,
    )

    if ok:
        return
    MonoSettings.create_new(get_monobank_public_key)
    ok = _verify_signature(
        request.headers["X-Sign"],
        request.body,
        MonoSettings.get_latest_or_add(get_monobank_public_key).public_key,
    )
    if not ok:
        raise Exception("Signature is not valid")


def create_invoice(order: Order, webhook_url):
    amount = 0
    basket_order = []
    for order_quantity in order.car_types.all():
        sum_ = order_quantity.car_type.price * order_quantity.quantity
        amount += sum_
        basket_order.append(
            {
                "name": order_quantity.car_type.name,
                "qty": order_quantity.quantity,
                "sum": sum_,
                "unit": "шт.",
            }
        )
    merchants_info = {
        "reference": str(order.id),
        "destination": "Покупка машин",
        "basketOrder": basket_order,
    }
    request_body = {
        "webHookUrl": webhook_url,
        "amount": amount,
        "merchantPaymInfo": merchants_info,
    }
    headers = {"X-Token": settings.MONOBANK_TOKEN}
    r = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        json=request_body,
        headers=headers,
    )
    r.raise_for_status()
    order.order_id = r.json()["invoiceId"]
    order.invoice_url = r.json()["pageUrl"]
    order.status = "created"
    order.save()
