import uuid

import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional

from ..settings.config import Config
import datetime

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()
square_client, square_location_id = config.get_square_connection()

@router.post("/create")
def create_order_object(orders: list = Form(...), ):
    """
    Create a new order object
    Comes from Order summary API
    :param orders: Contains the order details in the format [{"dish name": Pizza, "quantity": 1, "base price" :{ "amount": 100, "currency": "USD" }}, {"dish name": Burger, "quantity": 2, "base price" :{ "amount": 50, "currency": "USD" }}]
    :return:
    """
    result = square_client.orders.create_order(
        body={
            "order": {
                "location_id": square_location_id,
                "reference_id": str(uuid.uuid4()),
                "line_items":
                    orders
                ,
                "taxes": [
                    {
                        "uid": "state-sales-tax",
                        "name": "State Sales Tax",
                        "percentage": "10",
                        "scope": "ORDER"
                    }
                ],
            },
            "idempotency_key": "8193148c-9586-11e6-99f9-28cfe92138cf"
        }
    )

    if result.is_success():
        logger.info(f"Created Order Object")
    elif result.is_error():
        logger.error(f"Error in creating order -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/get")
def get_order_object(order_id: str = Form(...)):
    """
    Get order object
    :param order_id:
    :return: Order Objects
    """
    result = square_client.orders.retrieve_order(
        order_id=order_id
    )

    if result.is_success():
        logger.info(f"Get Order Object")
    elif result.is_error():
        logger.error(f"Error in getting order -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

@router.post("/pay")
def pay_order_object(order_id: str = Form(...), payment_ids : list = Form(...)):
    """
    Pay order object
    :param order_id:
    :return: Order Objects
    """
    result = square_client.orders.pay_order(
        order_id=order_id,
        body={
            "idempotency_key": str(uuid.uuid4()),
            "payment_ids": payment_ids
        }
    )

    if result.is_success():
        logger.info(f"Pay Order Object")
    elif result.is_error():
        logger.error(f"Error in paying order -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body

