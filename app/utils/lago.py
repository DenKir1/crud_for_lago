from typing import Dict

import requests
from fastapi import HTTPException
from lago_python_client import Client
from lago_python_client.exceptions import LagoApiError
from lago_python_client.models import Customer, Wallet, WalletTransaction, Metadata, CustomerBillingConfiguration, \
    MetadataList, BillableMetric
from starlette import status

from app.config.settings import settings


client = Client(api_key=settings.app.API_LAGO_KEY, api_url=settings.app.API_URL)
print(client.base_api_url)


def get_billable_metrics(code: str):
    try:
        metric = client.billable_metrics.find(code)
        print(f"Metric is got")
        return metric
    except LagoApiError as e:
        print(f"Metric is Not got")
        return
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        #                     detail=f"Bad news - {e}")


def get_or_create_billable_metric(name: str = "Your_metric", code: str = "your_code"):
    metric = get_billable_metrics(code)
    if metric:
        return metric

    billable_metric = BillableMetric(
        name=name,
        code=code,
        recurring=True,
        description='Membership fee',
        aggregation_type='unique_count_agg',
        field_name="user_id",
        filters=[], )

    try:
        metric = client.billable_metrics.create(billable_metric)
        print(f"Metric is created")
        return metric
    except LagoApiError as e:
        print(f"Metric is Not created")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Bad news - {e}")


def delete_metric(metric):
    metric_id = metric.code
    if not metric_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Metric is not deleted")
    try:
        client.billable_metrics.destroy(metric_id)
        print("Metric was deleted")
    except LagoApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Metric is not deleted - {e}")


def get_plan(name_code: str = "YourPlan_code") -> Dict | None:
    url = client.base_api_url + "plans" + f"/{name_code}"
    headers = {"Authorization": f"Bearer {settings.app.API_LAGO_KEY}", }

    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        print(f"Plan is got")
        return response.json()
    else:
        print(f"Plan is not got")
        return
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan was not found - {response.text}")


def get_or_create_plan(name: str = "YourPlan",
                       name_code: str = "YourPlan_code",
                       interval: str = "monthly",
                       amount_cents: int = 0,
                       amount_currency: str = "USD",
                       billable_id: str = "billable",
                       billable_code: str = "billable", ) -> Dict | None:

    plan_in = get_plan(name_code)
    if plan_in:
        return plan_in

    url = client.base_api_url + "plans"

    headers = {
        "Authorization": f"Bearer {settings.app.API_LAGO_KEY}",
        "Content-Type": "application/json"
    }

    payload = {"plan": {
        "charges": [
            {
                "billable_metric_id": billable_id,
                "billable_metric_code": billable_code,
                "charge_model": "standard",
                "invoiceable": True,
                "pay_in_advance": False,
                "prorated": True,
                "min_amount_cents": 0,
                "properties": {
                    "amount": "1"
                },
                "filters": [],
                "taxes": []
            }
        ],
        "name": name,
        "code": name_code,
        "interval": interval,
        "amount_cents": amount_cents,
        "amount_currency": amount_currency,
        "trial_period": 0.0,
        "pay_in_advance": True,
        "bill_charges_monthly": True,
        "minimum_commitment": {"amount_cents": 1}
    }}

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"Plan is created")
        return response.json()
    else:
        print(f"Plan is not created")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan was not created - {response.text}")


def delete_plan(plan: Dict | None):
    if not plan:
        print(f"Plan is not deleted")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan does not exist")

    plan_ = plan.get("plan")
    if not plan_:
        print(f"Plan is not deleted")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan does not exist")

    plan_code = plan_.get("code")
    if not plan_code:
        print(f"Plan is not deleted")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Plan")

    url = client.base_api_url + f"plans/{plan_code}"
    headers = {"Authorization": f"Bearer {settings.app.API_LAGO_KEY}", }

    response = requests.request("DELETE", url, headers=headers)
    if response.status_code == 200:
        print(f"Plan is deleted")
        return response.json()
    else:
        print(f"Plan is not deleted")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plan was not deleted")


def create_user_lago(user_id: str, name: str = "User"):
    # user_id - uuid str - sample - b111111-2222-3g33-4444-555f66f7777a
    metadata_object = Metadata(
        display_in_invoice=True,
        key='Create User',
        value='123456789'
    )

    customer = Customer(
        external_id=user_id,
        address_line1="5230 Penfield Ave",
        address_line2=None,
        city="Woodland Hills",
        currency="USD",
        country="US",
        email="test@example.com",
        legal_name="Coleman-Blair",
        legal_number="49-008-2965",
        tax_identification_number="EU123456789",
        logo_url="http://hooli.com/logo.png",
        name=name,
        phone="1-171-883-3711 x245",
        state="CA",
        timezone="Europe/Paris",
        url="http://hooli.com",
        zipcode="91364",
        billing_configuration=CustomerBillingConfiguration(
            invoice_grace_period=3,
            payment_provider="stripe",
            provider_customer_id="cus_12345",
            sync=True,
            sync_with_provider=True,
            document_locale="fr"
        ),
        metadata=MetadataList(__root__=[metadata_object])
    )

    try:
        user_in = client.customers.create(customer)
        if user_in.get("status_code") == 200:
            print("User was created")
            return user_in
        else:
            print("User was not created")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User was not created")
    except LagoApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad news - {e}")


def create_wallet_user(user_id: str):
    tariff = get_tariff_plan()
    wallet = Wallet(external_customer_id=user_id, **tariff)

    try:
        wallet = client.wallets.create(wallet)
        return wallet
    except LagoApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad news - {e}")


def get_tariff_plan(name: str = "TARIFF", rate: int = 1, curr: str = "USD"):
    return {
        "name": name,
        "rate_amount": rate,
        "paid_credits": "0.0",
        "granted_credits": "10.0",
        "currency": curr,
        "recurring_transaction_rules": [], }


def top_up_wallet(user_id: str, amount: int):
    wallet = get_wallet(user_id)

    transaction = WalletTransaction(
        wallet_id=wallet.lago_id,
        paid_credits=amount, )
    try:
        wallet = client.wallet_transactions.create(transaction)
        if wallet.status_code == 422:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Validation error")
    except LagoApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    return wallet


def get_wallet(user_id):
    create_wallet_user(user_id)
    try:
        wallet = client.wallets.find(user_id)
        if wallet.status_code == 404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet Not found")
        if wallet.status_code == 401:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not found")

    except LagoApiError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    return wallet


def withdraw_form_wallet(user_id: str, amount: int, type_: str):
    pass

