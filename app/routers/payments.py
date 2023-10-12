import uuid

import logging
from fastapi import APIRouter, Form, HTTPException, Header
from typing import Optional, Annotated, Union

from ..settings.config import Config
from ..utils.square_payments import get_square_connection

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()

# PAYMENT API
# need to add multiple payment types based on source_id
@router.post("/create")
def create_payment(access_token: Annotated[Union[str, None], Header()], source_id: str = Form(...), amount: int = Form(...), currency: Optional[str] = Form(None),
                   tip: Optional[int] = Form(None) , customer_id: str = Form(...)):
    """
    Create a payment
    :param source_id:
    :param currency:
    :param tip:
    :param customer_id:
    :param amount:
    :return: Payment Details
    """
    square_client, square_location_id = get_square_connection(access_token)
    reference_id = str(uuid.uuid4())
    idempotency = str(uuid.uuid4())
    result = square_client.payments.create_payment(
        body={
            "source_id": source_id,
            "idempotency_key": idempotency,
            "amount_money": {
                "amount": amount,
                "currency": currency or "USD",
            },
            "tip_money": {
                "amount": tip or 0,
                "currency": currency or "USD",
            },
            "autocomplete": True,
            "location_id": square_location_id,
            "reference_id": reference_id,
            "note": "Payment done for the order",
            "customer_id": customer_id,
        })
    if result.is_success():
        logger.info(f"Created Payment {reference_id}")
        return {"body": result.body, "reference_id": reference_id, "idempotency": idempotency, "status": "success"}
    elif result.is_error():
        logger.error(f"Error in creating Payment -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))


@router.post("/cancel")
def cancel_payment_by_idempotency(access_token: Annotated[Union[str, None], Header()], idempotency_key: str = Form(...)):
    """
    Cancel a payment
    :param idempotency_key:
    :return: Status of the cancellation
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.payments.cancel_payment_by_idempotency_key(
        body={
            "idempotency_key": idempotency_key
        }
    )

    if result.is_success():
        logger.info(f"Cancelled Payment")
        return {"body": "result.body", "status": "success"}
    elif result.is_error():
        logger.error(f"Error in cancelling Payment -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))


@router.post("/get")
def get_payment_by_id(access_token: Annotated[Union[str, None], Header()], payment_id: str = Form(...)):
    """
    Get a payment
    :param payment_id:
    :return: Payment Details
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.payments.get_payment(
        payment_id=payment_id
    )

    if result.is_success():
        logger.info(f"Get Payment")
        return {"body": result.body, "status": "success"}
    elif result.is_error():
        logger.error(f"Error in getting Payment -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))


@router.post("/update")
def update_payment_by_id(access_token: Annotated[Union[str, None], Header()], payment_id: str = Form(...), amount: int = Form(...), currency: Optional[str] = Form(None),
                         tip: Optional[int] = Form(None)):
    """
    Update a payment
    :param payment_id:
    :param amount:
    :param currency:
    :param tip:
    :return: Updated Payment Details
    """
    square_client, square_location_id = get_square_connection(access_token)
    idempotency = str(uuid.uuid4())
    result = square_client.payments.update_payment(
        payment_id=payment_id,
        body={
            "amount_money": {
                "amount": amount,
                "currency": currency or "USD",
            },
            "tip_money": {
                "amount": tip or 0,
                "currency": currency or "USD",
            },
            "idempotency_key": idempotency,
            "version": str(uuid.uuid4()),

        }
    )

    if result.is_success():
        logger.info(f"Updated Payment")
        return {"body": result.body, "status": "success"}
    elif result.is_error():
        logger.error(f"Error in updating Payment -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))


@router.post("/complete")
def complete_payment_by_id(access_token: Annotated[Union[str, None], Header()], payment_id: str = Form(...)):
    """
    Complete a payment
    :param payment_id:
    :return: Payment Details
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.payments.complete_payment(
        payment_id=payment_id,
        body={},
    )

    if result.is_success():
        logger.info(f"Completed Payment")
        return {"body": result.body, "status": "success"}
    elif result.is_error():
        logger.error(f"Error in completing Payment -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))
