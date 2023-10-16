import uuid
import datetime

import logging
from fastapi import APIRouter, Form, HTTPException, Header
from typing import Optional, Annotated, Union
import requests

from ..settings.config import Config
from ..utils.square_payments import get_square_connection

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()

@router.post("/create_customer")
def create_customer(access_token: Annotated[Union[str, None], Header()], first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), phone_number: str = Form(...), address_line_1: str = Form(...), address_line_2: Optional[str] = Form(None),  postal_code: str = Form(...), country: str = Form(...), birthday: str = Form(...),):
    """
    Create a new customer object with price
    :param access_token:
    :param first_name:
    :param last_name:
    :param email:
    :param phone_number:
    :param address_line_1:
    :param address_line_2:
    :param postal_code:
    :param country:
    :param birthday:
    :return:
    """
    #BIRTHDAY FORMAT YYYY-MM-DD
    if datetime.datetime.strptime(birthday, '%Y-%m-%d'):
        pass
    else:
        raise HTTPException(status_code=500, detail="Birthday format is not correct, please use YYYY-MM-DD")


    url = "https://connect.squareupsandbox.com/v2/customers"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }
    data = {
        "given_name": first_name,
        "family_name": last_name,
        "email_address": email,
        "phone_number": phone_number,
        "address": {
            "address_line_1": address_line_1,
            "address_line_2": address_line_2 or "",
            "postal_code": postal_code,
            "country": country
        },
        "birthday": birthday
    }

    response = requests.post(url, headers=headers, json=data)
    print(response)

    if response.status_code == 200:
        logger.info(f"Created Customer Object {first_name} {last_name}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in creating customer Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))





@router.post("/create")
def create_invoice_object(access_token: Annotated[Union[str, None], Header()],location_id: Annotated[Union[str, None], Header()], order_id: str = Form(...), reference_id: Optional[str] = Form(None), customer_id: str = Form(...)):
    """
    Create a new invoice object with price
    :param price:
    :param order_id:
    :param first_name:
    :param last_name:
    :param email:
    :param phone_number:
    :param reference_id:
    :return: Result of the creation
    """
    # square_client, square_location_id = get_square_connection(access_token)
    # result = square_client.invoice.create_invoice(
    #     body={
    #         "invoice": {
    #             "location_id": square_location_id,
    #             "order_id": order_id,
    #             "primary_recipient": {
    #                 "customer_id": str(uuid.uuid4()),
    #                 "given_name": first_name or None,
    #                 "email_address": email or None,
    #                 "phone_number": phone_number or None,
    #                 "family_name": last_name or None,
    #             },
    #             "payment_requests": [
    #                 {
    #                     "request_type": "BALANCE",
    #                     "due_date": datetime.datetime.now(),
    #                     "tipping_enabled": True,
    #                     "automatic_payment_source": None
    #                 }
    #             ],
    #             "delivery_method": "EMAIL",
    #             "invoice_number": "inv-" + order_id,
    #             "title": "Invoice for Order " + order_id,
    #             "description": "Invoice for Order " + order_id,
    #             "scheduled_at": datetime.datetime.now() + datetime.timedelta(days=1),
    #             "accepted_payment_methods": {
    #                 "card": True,
    #                 "cash": True,
    #                 "square_gift_card": True,
    #                 "bank_account": True,
    #                 "buy_now_pay_later": False,
    #                 "cash_app_pay": True
    #             },
    #             "custom_fields": [
    #                 {
    #                     "label": reference_id or str(uuid.uuid4()),
    #                     "value": "REF #" + (reference_id or str(uuid.uuid4())),
    #                     "placement": "ABOVE_LINE_ITEMS"
    #                 }
    #             ],
    #             "sale_or_service_date": datetime.datetime.now(),
    #             "store_payment_method_enabled": True,
    #             "idempotency_key": str(uuid.uuid4()),
    #     }
    #     }
    # )
    #
    # if result.is_success():
    #     logger.info(f"Created Invoice Object {order_id}")
    # elif result.is_error():
    #     logger.error(f"Error in creating invoice Item -->    {result.errors}")
    #     raise HTTPException(status_code=500, detail=str(result.errors))
    #
    # return result.body

    #schedule at
    date = datetime.datetime.now()
    rfc3339_date = date.isoformat() + "Z"
    print(rfc3339_date)

    #duedate is one day after schedule at and only Date in rfc3339 format
    due_date = date + datetime.timedelta(days=1)
    due_date = due_date.date()
    due_date = due_date.isoformat()
    print(due_date)


    url = "https://connect.squareupsandbox.com/v2/invoices"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }
    data = {"invoice": {
                "location_id": location_id,
                "order_id": order_id,
                "primary_recipient": {
                    "customer_id": customer_id,
                },
                "payment_requests": [
                    {
                        "request_type": "BALANCE",
                        "due_date": str(due_date),
                        "tipping_enabled": True,
                        "automatic_payment_source": "NONE"
                    }
                ],
                "delivery_method": "EMAIL",
                "invoice_number": "inv-" + order_id,
                "title": "Invoice for Order " + order_id,
                "description": "Invoice for Order " + order_id,
                "scheduled_at": str(rfc3339_date),
                "accepted_payment_methods": {
                    "card": True,
                },
        }
        }

    response = requests.post(url, headers=headers, json=data)
    print(response)

    if response.status_code == 200:
        logger.info(f"Created Invoice Object {order_id}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in creating invoice Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))


@router.post("/delete")
def delete_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_object_id: list = Form(...)):
    """
    Delete invoice object
    :param invoice_object_id:
    :return: Result of the deletion
    """
    url = f"https://connect.squareupsandbox.com/v2/invoices/{invoice_object_id}"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Deleted Invoice Object {invoice_object_id}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in deleting invoice Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))



@router.post("/get")
def get_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_id: str = Form(...)):
    """
    Get invoice object
    :param invoice_id:
    :return: Invoice Objects
    """
    url = f"https://connect.squareupsandbox.com/v2/invoices/{invoice_id}"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Get Invoice Object {invoice_id}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in getting invoice Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))


@router.post("/publish")
def publish_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_id: str = Form(...)):
    """
    Publish invoice object
    :param invoice_id:
    :return: Invoice Objects
    """
    url = f"https://connect.squareupsandbox.com/v2/invoices/{invoice_id}/publish"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }
    data = {
        "idempotency_key": str(uuid.uuid4()),
        "version": 1
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info(f"Publish Invoice Object {invoice_id}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in publishing invoice Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))



