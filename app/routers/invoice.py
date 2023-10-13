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

@router.post("/create")
def create_invoice_object(access_token: Annotated[Union[str, None], Header()], order_id: str = Form(...), first_name: Optional[str] = Form(None), last_name: Optional[str] = Form(None), email: Optional[str] = Form(None), phone_number: Optional[str] = Form(None), reference_id: Optional[str] = Form(None)):
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
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoice.create_invoice(
        body={
            "invoice": {
                "location_id": square_location_id,
                "order_id": order_id,
                "primary_recipient": {
                    "customer_id": str(uuid.uuid4()),
                    "given_name": first_name or None,
                    "email_address": email or None,
                    "phone_number": phone_number or None,
                    "family_name": last_name or None,
                },
                "payment_requests": [
                    {
                        "request_type": "BALANCE",
                        "due_date": datetime.datetime.now(),
                        "tipping_enabled": True,
                        "automatic_payment_source": None
                    }
                ],
                "delivery_method": "EMAIL",
                "invoice_number": "inv-" + order_id,
                "title": "Invoice for Order " + order_id,
                "description": "Invoice for Order " + order_id,
                "scheduled_at": datetime.datetime.now() + datetime.timedelta(days=1),
                "accepted_payment_methods": {
                    "card": True,
                    "cash": True,
                    "square_gift_card": True,
                    "bank_account": True,
                    "buy_now_pay_later": False,
                    "cash_app_pay": True
                },
                "custom_fields": [
                    {
                        "label": reference_id or str(uuid.uuid4()),
                        "value": "REF #" + (reference_id or str(uuid.uuid4())),
                        "placement": "ABOVE_LINE_ITEMS"
                    }
                ],
                "sale_or_service_date": datetime.datetime.now(),
                "store_payment_method_enabled": True,
                "idempotency_key": str(uuid.uuid4()),
        }
        }
    )

    if result.is_success():
        logger.info(f"Created Invoice Object {order_id}")
    elif result.is_error():
        logger.error(f"Error in creating invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/delete")
def delete_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_object_id: list = Form(...)):
    """
    Delete invoice object
    :param invoice_object_id:
    :return: Result of the deletion
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoice.delete_invoice(
        invoice_id=invoice_object_id
    )

    if result.is_success():
        logger.info(f"Deleted Invoice Object {invoice_object_id}")
    elif result.is_error():
        logger.error(f"Error in deleting invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/search")
def search_invoice_object(access_token: Annotated[Union[str, None], Header()], customer_id: str = Form(...)):
    """
    Search invoice objects
    :param customer_id:
    :return: Invoice Objects
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoices.search_invoices(
        body={
            "query": {
                "filter": {
                    "location_ids": [
                        square_location_id
                    ],
                    "customer_ids": [
                        customer_id
                    ]
                },
                "sort": {
                    "field": "INVOICE_SORT_DATE",
                    "order": "DESC"
                }
            }
        }
    )

    if result.is_success():
        logger.info(f"Search Invoice Object")
    elif result.is_error():
        logger.error(f"Error in searching invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/get")
def get_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_id: str = Form(...)):
    """
    Get invoice object
    :param invoice_id:
    :return: Invoice Objects
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoice.get_invoice(
        invoice_id=invoice_id
    )

    if result.is_success():
        logger.info(f"Get Invoice Object")
    elif result.is_error():
        logger.error(f"Error in getting invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/publish")
def publish_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_id: str = Form(...)):
    """
    Publish invoice object
    :param invoice_id:
    :return: Invoice Objects
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoice.publish_invoice(
        invoice_id=invoice_id,
        body={
            "version": 1,
            "idempotency_key": str(uuid.uuid4())}
    )

    if result.is_success():
        logger.info(f"Publish Invoice Object")
    elif result.is_error():
        logger.error(f"Error in publishing invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/cancel")
def cancel_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_id: str = Form(...), version: int = Form(...)):
    """
    Cancel invoice object
    :param invoice_id:
    :return: Invoice Objects
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoice.cancel_invoice(
        invoice_id=invoice_id,
        body={
            "version": version,}
    )

    if result.is_success():
        logger.info(f"Cancel Invoice Object")
    elif result.is_error():
        logger.error(f"Error in cancelling invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/update")
def update_invoice_object(access_token: Annotated[Union[str, None], Header()], invoice_id: str = Form(...), version: int = Form(...), first_name: Optional[str] = Form(None), last_name: Optional[str] = Form(None), email: Optional[str] = Form(None), phone_number: Optional[str] = Form(None), reference_id: Optional[str] = Form(None)):
    """
    Update invoice object
    :param invoice_id:
    :return: Invoice Objects
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.invoice.update_invoice(
        invoice_id=invoice_id,
        body={
            "version": version,
            "invoice": {
                "primary_recipient": {
                    "given_name": first_name or None,
                    "email_address": email or None,
                    "phone_number": phone_number or None,
                    "family_name": last_name or None,
                },
                "custom_fields": [
                    {
                        "label": reference_id or str(uuid.uuid4()),
                        "value": "REF #" + (reference_id or str(uuid.uuid4())),
                        "placement": "ABOVE_LINE_ITEMS"
                    }
                ],
            }
        }
    )

    if result.is_success():
        logger.info(f"Update Invoice Object")
    elif result.is_error():
        logger.error(f"Error in updating invoice Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body
