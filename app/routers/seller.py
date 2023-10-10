import logging

from fastapi import APIRouter, Form, HTTPException
from langchain.prompts import PromptTemplate
from ..settings.config import Config

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config.get_instance()
conn = config.get_postgres_connection()
llm = config.get_vertex_ai_connection()

router = APIRouter()

@router.post("/recommend_menu", tags=["seller"])
def recommend_menu(preferred_cuisine: str = Form(...), prep_time_breakfast: str = Form(...),
                   prep_time_lunch: str = Form(...), prep_time_dinner: str = Form(...),
                   cook_time_breakfast: str = Form(...), cook_time_lunch: str = Form(...),
                   cook_time_dinner: str = Form(...)):
    """
    Recommend menu using Vertex AI
    :param cook_time_dinner:
    :param preferred_cuisine:
    :param prep_time_breakfast:
    :param prep_time_lunch:
    :param prep_time_dinner:
    :return: Detailed Menu JSON
    """
    logger.info(f"Reading ingredients from Ingredient table of postgres")
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Ingredients")
        rows = cur.fetchall()
        # Column Names - id, Created_at,ingredient_name,ingredient_type, ingredient_sub_type, shelf_life_days, quantity, unit
        logger.info(f"Total number of ingredients in the table: {len(rows)}")
        # Create a list of Dictionary of Ingredients with Name, quantity unit, shelf life days, ingredient type,
        # ingredient sub type
        ingredients = []
        for row in rows:
            ingredient = {}
            ingredient['name'] = row[2]
            ingredient['quantity'] = row[6]
            ingredient['unit'] = row[7]
            ingredient['shelf_life_days'] = row[5]
            ingredient['ingredient_type'] = row[3]
            ingredient['ingredient_sub_type'] = row[4]
            ingredients.append(ingredient)
        logger.info(f"Read ingredients from Postgres")

    except Exception as e:
        # Raise HTTP exception
        logger.exception(f"An Exception Occurred while reading ingredients from Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Pass the list to Context and generate the menu
    template = f""" Context: You are a chef of a {preferred_cuisine} restaurant. You are planning to prepare a menu for the restaurant. Here is the list of ingredients you have in your kitchen: {ingredients}. Please prepare a {preferred_cuisine} menu for the restaurant. You always have flour, water, spices, milk, curd, onion, tomato, ginger, garlic, oil, butter, ghee in your inventory,
     Task: Prepare a menu with multiple choices, atleast 15 each for Breakfast, Lunch, Dinner, Dessert, Drinks, Sides, Breads. Atleast 10 dishes for each category. You can customize the menu as per your requirement. 
     Answer: Provide the Menu in JSON format {"Course1":[dish1:{"Customization":[option1,option2]},dish2]},"Course2":[dish3,dish4]}} along with customizations if any based on Ingredients. For example: {"Breakfast":[Aalo Pranthe:[Customization: Paneer, Gobi, No Onion], Poha, Upma, Idli, Dosa, Uttapam, Bread Toast:[Customization: Brown Bread, White Bread], Parle G, Cornflakes, Oats], "Lunch":[Rice, Roti, Dal, Sabji, Salad, Raita, Papad, Pickle, Curd, Chutney], "Dinner":[Rice, Roti, Dal, Sabji, Salad, Raita, Papad, Pickle, Curd, Chutney], "Dessert":[Ice Cream, Cake, Pie, Cookies, Pudding, Fruit, Gulab Jamun, Rasgulla, Kheer, Jalebi], "Drinks":[Coffee, Tea, Juice, Milk, Soda, Water, Beer, Wine, Liquor, Lassi], "Sides":[Curd, Raita, Pappad, Salad], "Breads":[Naan,Roti, Tandoori Roti, Garlic Naan]}
     Constraints: Keep in mind the menu should be {preferred_cuisine} menu and prepration time of breakfast menu should be less than equal to {prep_time_breakfast}, lunch menu should be less than equal to {prep_time_lunch}, dinner menu should be less than equal to {prep_time_dinner}, cook time of breakfast menu should be less than equal to {cook_time_breakfast}, cook time of lunch menu should be less than equal to {cook_time_lunch} and cook time of dinner menu should be less than equal to {cook_time_dinner}.
     Definations: Prep time is the time taken to prepare the dish. Cook time is the time taken to cook the dish.
     """

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm

    # Generate the menu
    try:
        return chain.invoke({'preferred_cuisine': preferred_cuisine, 'ingredients': ingredients,
                             'prep_time_breakfast': prep_time_breakfast, 'prep_time_lunch': prep_time_lunch,
                             'prep_time_dinner': prep_time_dinner, 'cook_time_breakfast': cook_time_breakfast,
                             'cook_time_lunch': cook_time_lunch, 'cook_time_dinner': cook_time_dinner})
    except Exception as e:
        logger.exception(f"An Exception Occurred while generating menu using Vertex AI --> {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Read All ingredients from Ingredient table of postgres, and recommend menu using Vertex AI
@router.post("/add_ingedients", tags=["seller"])
def add_ingedients(ingredient_name: str = Form(...), ingredient_type: str = Form(...),
                   ingredient_sub_type: str = Form(...), shelf_life_days: str = Form(...), quantity: str = Form(...),
                   unit: str = Form(...)):
    """
    Add ingredients to Ingredient table of postgres
    :param ingredient_name:
    :param ingredient_type:
    :param ingredient_sub_type:
    :param shelf_life_days:
    :param quantity:
    :param unit:
    :return: Success message
    """
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Ingredients (ingredient_name,ingredient_type,ingredient_sub_type,shelf_life_days,quantity,unit) VALUES (%s, %s, %s, %s, %s, %s)",
            (ingredient_name, ingredient_type, ingredient_sub_type, shelf_life_days, quantity, unit))
        conn.commit()
        logger.info(f"Added ingredients to Postgres")
        return {"message": "Ingredient added successfully"}
    except Exception as e:
        # Raise HTTP exception
        logger.exception(f"An Exception Occurred while adding ingredients to Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reengineer_dish", tags=["seller"])
def reengineer_dish(dish_name: str = Form(...), preferred_cuisine: str = Form(...)):
    """
    Reengineer the dish with same ingredients
    :param dish_name:
    :return: New dish name
    """
    template = f""" Context: You are a chef of a {preferred_cuisine} restaurant. You are given a dish that you need to reengineer. Please recommend some other dish, that has same ingredients as {dish_name}. You always have flour, water, spices, milk, curd, onion, tomato, ginger, garlic, oil, butter, ghee in your inventory,
        Task: Reengineer the dish with same ingredients. 
        Answer: Provide the dish name. For example: Aalo Pranthe
        Constraints: Keep in mind the dish should be {preferred_cuisine} dish and prepration and cook time of new and old dish should be similar.
        Definations: Prep time is the time taken to prepare the dish. Cook time is the time taken to cook the dish."""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    try:
        return chain.invoke({'dish_name': dish_name, 'preferred_cuisine': preferred_cuisine})
    except Exception as e:
        logger.exception(f"An Exception Occurred while reengineering dish using Vertex AI --> {e}")
        raise HTTPException(status_code=500, detail=str(e))
