import uuid
import os
import json

import logging
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Header
from typing import Optional, Annotated, Union
import requests

from ..settings.config import Config
# from ..utils.square_payments import get_square_connection

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
    # square_client, square_location_id = get_square_connection(access_token)
    # print(square_client, square_location_id)
    # result = square_client.catalog.upsert_catalog_object(
    #     body={
    #         "idempotency_key": str(uuid.uuid4()),
    #         "object": {
    #             "type": "ITEM",
    #             "id": "#" + name,
    #             "item_data": {
    #                 "name": name,
    #                 "abbreviation": name[0:3],
    #                 "variations": [
    #                     {
    #                         "type": "ITEM_VARIATION",
    #                         "id": "#" + name + "_variation",
    #                         "item_data": {
    #                             "name": name,
    #                         },
    #                         "item_variation_data": {
    #                             "pricing_type": "FIXED_PRICING",
    #                             "price_money": {
    #                                 "amount": price,
    #                                 "currency": "CAD"
    #                             },
    #                         "available_for_booking": False
    #                         }
    #                     }
    #                 ]
    #             },
    #
    #
    #         }
    #     }
    # )
    url = "https://connect.squareupsandbox.com/v2/catalog/object"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer "+access_token,
        "Content-Type": "application/json"
    }
    data = {
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

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info(f"Created Catalog Object {name}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in creating catalog Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))



@router.post("/delete")
def delete_catalog_object(access_token: Annotated[Union[str, None], Header()], catalog_object_id: list = Form(...)):
    """
    Delete catalog object
    :param catalog_object_id:
    :return: Result of the deletion
    """
    # square_client, square_location_id = get_square_connection(access_token)
    # result = square_client.catalog.delete_catalog_object(
    #     object_id=catalog_object_id
    # )
    #
    # if result.is_success():
    #     logger.info(f"Deleted Catalog Object {catalog_object_id}")
    # elif result.is_error():
    #     logger.error(f"Error in deleting catalog Item -->    {result.errors}")
    #     raise HTTPException(status_code=500, detail=str(result.errors))
    #
    # return result.body

    url = f"https://connect.squareupsandbox.com/v2/catalog/object/{catalog_object_id}"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Deleted Catalog Object {catalog_object_id}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in deleting catalog Item -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))



@router.post("/list")
def list_catalog_objects(access_token: Annotated[Union[str, None], Header()]):
    """
    List catalog objects
    :param types:
    :return: Catalog Objects
    """
    # square_client, square_location_id = get_square_connection(access_token)
    #
    # result = square_client.catalog.list_catalog(
    #     types="ITEM"
    # )
    #
    # if result.is_success():
    #     logger.info(f"Listed Catalog Objects")
    # elif result.is_error():
    #     logger.error(f"Error in listing catalog Items -->    {result.errors}")
    #     raise HTTPException(status_code=500, detail=str(result.errors))
    #
    # return result.body

    url = "https://connect.squareupsandbox.com/v2/catalog/list?types=ITEM"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    print(response)

    if response.status_code == 200:
        logger.info(f"Listed Catalog Objects")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in listing catalog Items -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))


@router.post("/create/image")
def create_catalog_image(access_token: Annotated[Union[str, None], Header()], catalog_object_id: str = Form(...), imageurl: str = Form(...), dishname: str = Form(...)):
    """
    Create a catalog image
    :param catalog_object_id:
    :param image:
    :return: Object data from Catalog
    """

    # if image.content_type != "image/jpeg":
    #     raise HTTPException(status_code=400, detail="Only JPEG images are supported")


    image = requests.get(imageurl)
    if image.status_code != 200:
        raise HTTPException(status_code=400, detail="Image URL is not valid")
    else:
        logger.info(f"Image URL is valid")
        temp_image_file = "temp_image"+str(uuid.uuid4())+".jpg"
        with open(temp_image_file, 'wb') as f:
            f.write(image.content)
        logger.info(f"Image downloaded")


    url = "https://connect.squareupsandbox.com/v2/catalog/images"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token
    }
    data = {
        "idempotency_key": str(uuid.uuid4()),
        "object_id": catalog_object_id,
        "image": {
            "type": "IMAGE",
            "id": "#TEMP_ID",
            "image_data": {
                "caption": "A picture of a "+dishname,
            }
        }
    }
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')


    form_data = {
        'json': (None, json_data, 'application/json'),
        'image': (None, open(temp_image_file, 'rb'), 'image/jpeg'),  # Adjust the content type as needed
    }

    response = requests.post(url, headers=headers,files=form_data)
    #remove temp image file
    os.remove(temp_image_file)

    if response.status_code == 200:
        logger.info(f"Created Catalog Image {catalog_object_id}")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in creating catalog Image -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))


