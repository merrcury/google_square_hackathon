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

@router.post("/create")
def add_ingredients(name: str = Form(...), quantity: int = Form(...), unit: str = Form(...),
                    shelf_life_days: int = Form(...), ingredient_type: str = Form(...),
                    ingredient_sub_type: str = Form(...)):
    """
    Add Ingredients to Postgres Supabase
    :param name:
    :param quantity:
    :param unit:
    :param shelf_life_days:
    :param ingredient_type:
    :param ingredient_sub_type:
    :return:
    """

    try:
        logger.info(f"Adding Ingredients to Postgres")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Ingredients (name, quantity, unit, shelf_life_days, ingredient_type, ingredient_sub_type) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, quantity, unit, shelf_life_days, ingredient_type, ingredient_sub_type))
        conn.commit()
        logger.info(f"Added Ingredients to Postgres")
    except Exception as e:
        logger.exception(f"An Exception Occurred while adding Ingredients to Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {'message': "Added Ingredients to Postgres", 'status': 'success'}


@router.post("/read")
def read_ingredients():
    """
    Read Ingredients from Postgres Supabase
    :return: Ingredients JSON
    """
    try:
        logger.info(f"Reading Ingredients from Postgres")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Ingredients")
        rows = cur.fetchall()
        logger.info(f"Read Ingredients from Postgres")
        ingredients = []
        for row in rows:
            ingredient = {'name': row[1], 'quantity': row[2], 'unit': row[3], 'shelf_life_days': row[4],
                          'ingredient_type': row[5], 'ingredient_sub_type': row[6]}
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
        cur.execute("DELETE FROM Ingredients WHERE name = %s", (name,))
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
        cur.execute("UPDATE Ingredients SET quantity = %s WHERE name = %s", (quantity, name))
        conn.commit()
        logger.info(f"Updated Ingredients quantity in Postgres")
    except Exception as e:
        logger.exception(f"An Exception Occurred while updating Ingredients quantity in Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {'message': "Updated Ingredients quantity in Postgres", 'status': 'success'}


@router.post("/update")
def update_ingredients(name: str = Form(...), quantity: int = Form(...), unit: str = Form(...),
                       shelf_life_days: int = Form(...), ingredient_type: str = Form(...),
                       ingredient_sub_type: str = Form(...)):
    """
    Update Ingredients in Postgres Supabase
    :param name:
    :param quantity:
    :param unit:
    :param shelf_life_days:
    :param ingredient_type:
    :param ingredient_sub_type:
    :return:
    """
    try:
        logger.info(f"Updating Ingredients in Postgres")
        cur = conn.cursor()
        cur.execute(
            "UPDATE Ingredients SET quantity = %s, unit = %s, shelf_life_days = %s, ingredient_type = %s, "
            "ingredient_sub_type = %s WHERE name = %s",
            (quantity, unit, shelf_life_days, ingredient_type, ingredient_sub_type, name))
        conn.commit()
        logger.info(f"Updated Ingredients in Postgres")
    except Exception as e:
        logger.exception(f"An Exception Occurred while updating Ingredients in Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {'message': "Updated Ingredients in Postgres", 'status': 'success'}


@router.post("/update/shelf_life_days")
def update_ingredients_shelf_life_days(name: str = Form(...), shelf_life_days: int = Form(...)):
    """
    Update Ingredients shelf life days in Postgres Supabase
    :param name:
    :param shelf_life_days:
    :return:
    """
    try:
        logger.info(f"Updating Ingredients shelf life days in Postgres")
        cur = conn.cursor()
        cur.execute("UPDATE Ingredients SET shelf_life_days = %s WHERE name = %s", (shelf_life_days, name))
        conn.commit()
        logger.info(f"Updated Ingredients shelf life days in Postgres")
    except Exception as e:
        logger.exception(f"An Exception Occurred while updating Ingredients shelf life days in Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {'message': "Updated Ingredients shelf life days in Postgres", 'status': 'success'}

