import uuid

import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional

from ..settings.config import Config

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()
square_client, square_location_id = config.get_square_connection()


@router.post("/create")
def create_catalog_object(name: str = Form(...), price: int = Form(...)):
    """
    Create a new catalog object with price
    :param name:
    :param price:
    :return: Catalog Object Details including catalog_object_id
    """
    result = square_client.catalog.upsert_catalog_object(
        body={
            "idempotency_key": str(uuid.uuid4()),
            "object": {
                "type": "ITEM",
                "id": "#" + name,
                "item_data": {
                    "name": name,
                    "description": price,
                    "abbreviation": name[0:3],

                }

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
def delete_catalog_object(catalog_object_id: list = Form(...)):
    """
    Delete catalog object
    :param catalog_object_id:
    :return: Result of the deletion
    """
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
def list_catalog_objects(types: Optional[list] = Form(None)):
    """
    List catalog objects
    :param types:
    :return: Catalog Objects
    """
    if types is None:
        types = ["ITEM"]
    result = square_client.catalog.list_catalog(
        types=types
    )

    if result.is_success():
        logger.info(f"Listed Catalog Objects")
    elif result.is_error():
        logger.error(f"Error in listing catalog Items -->    {result.errors}")
        raise HTTPException(status_code=500, detail=str(result.errors))

    return result.body


@router.post("/create/image")
def create_catalog_image(catalog_object_id: str = Form(...), image: UploadFile = File(...)):
    """
    Create a catalog image
    :param catalog_object_id:
    :param image:
    :return: Object data from Catalog
    """
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
