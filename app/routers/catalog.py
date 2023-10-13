import uuid

import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Header
from typing import Optional, Annotated, Union


from ..settings.config import Config
from ..utils.square_payments import get_square_connection

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()


@router.post("/create")
def create_catalog_object(access_token: Annotated[Union[str, None], Header()],  name: str = Form(...), price: int = Form(...)):
    """
    Create a new catalog object with price
    :param name:
    :param price:
    :return: Catalog Object Details including catalog_object_id
    """
    square_client, square_location_id = get_square_connection(access_token)
    print(square_client, square_location_id)
    result = square_client.catalog.upsert_catalog_object(
        body={
            "idempotency_key": str(uuid.uuid4()),
            "object": {
                "type": "ITEM",
                "id": "#" + name,
                "item_data": {
                    "name": name,
                    "abbreviation": name[0:3],
                    "variations": [
                        {
                            "type": "ITEM_VARIATION",
                            "id": "#" + name + "_variation",
                            "item_data": {
                                "name": name,
                            },
                            "item_variation_data": {
                                "pricing_type": "FIXED_PRICING",
                                "price_money": {
                                    "amount": price,
                                    "currency": "CAD"
                                },
                            "available_for_booking": False
                            }
                        }
                    ]
                },


            }
        }
    )

    if result.is_success():
        logger.info(f"Created Catalog Object {name}")
    elif result.is_error():
        logger.error(f"Error in creating catalog Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body


@router.post("/delete")
def delete_catalog_object(access_token: Annotated[Union[str, None], Header()], catalog_object_id: list = Form(...)):
    """
    Delete catalog object
    :param catalog_object_id:
    :return: Result of the deletion
    """
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.catalog.delete_catalog_object(
        object_id=catalog_object_id
    )

    if result.is_success():
        logger.info(f"Deleted Catalog Object {catalog_object_id}")
    elif result.is_error():
        logger.error(f"Error in deleting catalog Item -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body


@router.post("/list")
def list_catalog_objects(access_token: Annotated[Union[str, None], Header()]):
    """
    List catalog objects
    :param types:
    :return: Catalog Objects
    """
    square_client, square_location_id = get_square_connection(access_token)

    result = square_client.catalog.list_catalog(
        types="ITEM"
    )

    if result.is_success():
        logger.info(f"Listed Catalog Objects")
    elif result.is_error():
        logger.error(f"Error in listing catalog Items -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body


@router.post("/create/image")
def create_catalog_image(access_token: Annotated[Union[str, None], Header()], catalog_object_id: str = Form(...), image: UploadFile = File(...)):
    """
    Create a catalog image
    :param catalog_object_id:
    :param image:
    :return: Object data from Catalog
    """
    if image.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail="Only JPEG images are supported")
    square_client, square_location_id = get_square_connection(access_token)
    result = square_client.catalog.create_catalog_image(
        request={
            "idempotency_key": str(uuid.uuid4()),
            "object_id": catalog_object_id,
            "image": {
                "type": "IMAGE",
                "id": "#TEMP_ID",
                "image_data": {
                    "caption": "A picture of a cup of coffee"
                }
            }
        },
        file=image.file
    )

    if result.is_success():
        logger.info(f"Created Catalog Image {catalog_object_id}")
    elif result.is_error():
        logger.error(f"Error in creating catalog Image -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body
