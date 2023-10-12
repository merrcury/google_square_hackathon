import uuid

import logging
import json
from fastapi import APIRouter, Form, HTTPException

from ..settings.config import Config

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
config = Config.get_instance()
conn = config.get_postgres_connection()

@router.post("/read")
def read_ingredients():
    """
    Read Ingredients from Postgres Supabase
    :return: Ingredients JSON
    """
    try:
        logger.info(f"Reading Ingredients from Postgres")
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM "Ingredients" """)
        rows = cur.fetchall()
        logger.info(f"Read Ingredients from Postgres")
        ingredients = []
        for row in rows:
            ingredient = {'name': row[2], 'quantity': row[6], 'unit': row[8], 'shelf_life_days': row[5],
                          'ingredient_type': row[3], 'ingredient_sub_type': row[4], 'ingredient_id': row[0], 'unitprice': row[7] }
            ingredients.append(ingredient)
        return json.dumps(ingredients)
    except Exception as e:
        logger.exception(f"An Exception Occurred while reading Ingredients from Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete")
def delete_ingredients(name: str = Form(...)):
    """
    Delete Ingredients from Postgres Supabase
    :param name:
    :return:
    """
    try:
        logger.info(f"Deleting Ingredients from Postgres")
        cur = conn.cursor()
        cur.execute(""" DELETE FROM "Ingredients" WHERE ingredient_name = %s""", (name,))
        conn.commit()
        logger.info(f"Deleted Ingredients from Postgres")
    except Exception as e:
        logger.exception(f"An Exception Occurred while deleting Ingredients from Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {'message': "Deleted Ingredients from Postgres", 'status': 'success'}


@router.post("/update/quantity")
def update_ingredients_quantity(name: str = Form(...), quantity: int = Form(...)):
    """
    Update Ingredients quantity in Postgres Supabase
    :param name:
    :param quantity:
    :return:
    """
    try:
        logger.info(f"Updating Ingredients quantity in Postgres")
        cur = conn.cursor()
        cur.execute(""" UPDATE "Ingredients" SET quantity = %s WHERE ingredient_name = %s""", (quantity, name))
        conn.commit()
        logger.info(f"Updated Ingredients quantity in Postgres")
    except Exception as e:
        logger.exception(f"An Exception Occurred while updating Ingredients quantity in Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {'message': "Updated Ingredients quantity in Postgres", 'status': 'success'}

