import uuid

import logging
from fastapi import APIRouter, Form, HTTPException, Header
from typing import Annotated, Union
import requests
import json

from ..settings.config import Config
from ..utils.square_payments import get_square_connection

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()

@router.post("/create")
def create_order_object(access_token: Annotated[Union[str, None], Header()], location_id: Annotated[Union[str, None], Header()], orders: list = Form(...), customer_id: str = Form(...) ):
    """
    Create a new order object
    Comes from Order summary API
    :param orders: Contains the order details in the format [{"name": "Aalo prantha","quantity": "1", "base_price_money": { "amount": 20,"currency": "CAD"}}]
    :return:
    """
    # square_client, square_location_id = get_square_connection(access_token)
    # result = square_client.orders.create_order(
    #     body={
    #         "order": {
    #             "location_id": square_location_id,
    #             "reference_id": str(uuid.uuid4()),
    #             "line_items":
    #                 orders
    #             ,
    #             "taxes": [
    #                 {
    #                     "uid": "state-sales-tax",
    #                     "name": "State Sales Tax",
    #                     "percentage": "10",
    #                     "scope": "ORDER"
    #                 }
    #             ],
    #         },
    #         "idempotency_key": "8193148c-9586-11e6-99f9-28cfe92138cf"
    #     }
    # )
    #
    #
    # if result.is_success():
    #     logger.info(f"Created Order Object")
    # elif result.is_error():
    #     logger.error(f"Error in creating order -->    {result.errors}")
    #     raise HTTPException(status_code=500, detail=str(result.errors))
    #
    # return result.body

    url = "https://connect.squareupsandbox.com/v2/orders"
    headers = {
        'square-version': '2021-05-13',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    orders_post=[]
    if type(orders[0])==dict:
        orders_post = orders
    elif type(orders[0])==str:
        for order in orders:
            orders_post.append(json.loads(order))


    data = {
        "order": {
            "location_id": location_id ,
            "customer_id": customer_id,
            "reference_id": str(uuid.uuid4()),
            "line_items":
                orders_post
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

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info(f"Created Order Object")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in creating order -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))

@router.post("/get")
def get_order_object(access_token: Annotated[Union[str, None], Header()], order_id: str = Form(...)):
    """
    Get order object
    :param order_id:
    :return: Order Objects
    """
    # square_client, square_location_id = get_square_connection(access_token)
    # result = square_client.orders.retrieve_order(
    #     order_id=order_id
    # )
    #
    # if result.is_success():
    #     logger.info(f"Get Order Object")
    # elif result.is_error():
    #     logger.error(f"Error in getting order -->    {result.errors}")
    #     raise HTTPException(status_code=500, detail=str(result.errors))
    #
    # return result.body

    url = f"https://connect.squareupsandbox.com/v2/orders/{order_id}"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Get Order Object")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in getting order -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))

@router.post("/pay")
def pay_order_object(access_token: Annotated[Union[str, None], Header()], order_id: str = Form(...), payment_ids : list = Form(...)):
    """
    Pay order object
    :param order_id:
    :return: Order Objects
    """
    # square_client, square_location_id = get_square_connection(access_token)
    # result = square_client.orders.pay_order(
    #     order_id=order_id,
    #     body={
    #         "idempotency_key": str(uuid.uuid4()),
    #         "payment_ids": payment_ids
    #     }
    # )
    #
    # if result.is_success():
    #     logger.info(f"Pay Order Object")
    # elif result.is_error():
    #     logger.error(f"Error in paying order -->    {result.errors}")
    #     raise HTTPException(status_code=500, detail=str(result.errors))
    #
    # return result.body

    url = f"https://connect.squareupsandbox.com/v2/orders/{order_id}/pay"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    data = {
        "idempotency_key": str(uuid.uuid4()),
        "payment_ids": payment_ids
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info(f"Pay Order Object")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in paying order -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))
