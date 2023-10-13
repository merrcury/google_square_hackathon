import logging
import json

from fastapi import APIRouter, Form, HTTPException
from langchain.prompts import PromptTemplate
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.chains import LLMChain

from ..settings.config import Config
from ..utils.clean import cleaned
from typing import Optional


# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config.get_instance()
conn = config.get_postgres_connection()
llm = config.get_vertex_ai_connection()
dalle_llm = config.get_open_ai_connection()

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
    :param cook_time_breakfast:
    :param cook_time_lunch:
    :param cook_time_dinner:
    :return: Detailed Menu JSON
    """
    logger.info(f"Reading ingredients from Ingredient table of postgres")
    try:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM "Ingredients" """)
        rows = cur.fetchall()
        # Column Names - id, Created_at,ingredient_name,ingredient_type, ingredient_sub_type, shelf_life_days, quantity, unit
        logger.info(f"Total number of ingredients in the table: {len(rows)}")
        # Create a list of Dictionary of Ingredients with Name, quantity unit, shelf life days, ingredient type,
        # ingredient sub type
        ingredients = []
        for row in rows:
            ingredient = {'name': row[2], 'quantity': row[6], 'unit': row[8], 'shelf_life_days': row[5],
                          'ingredient_type': row[3], 'ingredient_sub_type': row[4], 'ingredient_id': row[0],
                          'unitprice': row[7]}
            ingredients.append(ingredient)
        logger.info(f"Read ingredients from Postgres")

    except Exception as e:
        # Raise HTTP exception
        logger.exception(f"An Exception Occurred while reading ingredients from Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

    # Pass the list to Context and generate the menu
    template = """ Context: You are a chef of a {preferred_cuisine} restaurant. You are planning to prepare a menu for the restaurant. Here is the list of ingredients you have in your kitchen: {ingredients}. Each ingredient has a unit price. Please prepare a {preferred_cuisine} menu for the restaurant. You always have flour, water, spices, milk, curd, onion, tomato, ginger, garlic, oil, butter, ghee in your inventory,
     Task: Prepare a menu with multiple choices, atleast 15 each for Breakfast, Lunch, Dinner, Dessert, Drinks, Sides, Breads. Atleast 10 dishes for each category. You can customize the menu as per your requirement. Mention the Price with each dish
     Price calculation of 1 ingredient: Price of 1 ingredient is calculated as per the formula: Price = (Quantity * Unit Price)  Example use 2 potato for 1 serve of Aloprantha, cost of 1 potato is 10, then price of potato in 1 serve of Aloprantha is 20, similarly calculate for all ingredients
     Price Calculation of Dish: Price of the dish is calculated as per the formula: Price = (Sum of Price of all ingredients + 30% of Sum of Price of all ingredients + 5% of Sum of Price of all Ingredients) + 10% tax example if price of all ingredients  required to make Alo prantha is 100, then price of Alo prantha is 100 + 30 + 5 = 135 + 10% tax = 148.5
     Answer: Provide the Menu in JSON key-value pairs without special chars  format "Course1":dish1:"Customization":option1,option2,"price":amount,dish2:"price":amount,"Course2":dish3:"price":amount,dish4:"price":amount along with customizations if any based on Ingredients. For example: "Breakfast":dish 1:Customization: custom1 ,price:x, dish2:price:y, "Lunch":dish3:price:z, dish4:price:z, "Dinner":dish5:price:z, dish6:price:z, "Dessert":dish7:price:z, dish8:price:z, "Drinks":dish9:price:z, dish10:price:z, "Sides":dish11:price:z, dish12:price:z, "Breads":dish13:price:z, dish14:price:z
     Constraints: Keep in mind the menu should be {preferred_cuisine} menu and prepration time of breakfast menu should be less than equal to {prep_time_breakfast}, lunch menu should be less than equal to {prep_time_lunch}, dinner menu should be less than equal to {prep_time_dinner}, cook time of breakfast menu should be less than equal to {cook_time_breakfast}, cook time of lunch menu should be less than equal to {cook_time_lunch} and cook time of dinner menu should be less than equal to {cook_time_dinner}. Do include estimated Price of the dish in the menu.
     Definations: Prep time is the time taken to prepare the dish. Cook time is the time taken to cook the dish.
     """

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm

    # Generate the menu
    try:
        s =  chain.invoke({'preferred_cuisine': preferred_cuisine, 'ingredients': ingredients,
                             'prep_time_breakfast': prep_time_breakfast, 'prep_time_lunch': prep_time_lunch,
                             'prep_time_dinner': prep_time_dinner, 'cook_time_breakfast': cook_time_breakfast,
                             'cook_time_lunch': cook_time_lunch, 'cook_time_dinner': cook_time_dinner})
        return(cleaned(s))
    except Exception as e:
        logger.exception(f"An Exception Occurred while generating menu using Vertex AI --> {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Read All ingredients from Ingredient table of postgres, and recommend menu using Vertex AI
@router.post("/add_ingedients", tags=["seller"])
def add_ingedients(ingredient_name: str = Form(...), ingredient_type: str = Form(...),
                   ingredient_sub_type: str = Form(...), shelf_life_days: str = Form(...), quantity: str = Form(...),
                   unit: str = Form(...), unitprice: Optional[str]=Form(None) ):
    """
    Add ingredients to Ingredient table of postgres
    :param ingredient_name:
    :param ingredient_type:
    :param ingredient_sub_type:
    :param shelf_life_days:
    :param quantity:
    :param unit:
    :param unitprice:
    :return: Success message
    """
    try:
        #dataprocessing
        if unitprice is None:
            unitprice = 2
        ingredient_name = ingredient_name.lower()
        ingredient_type = ingredient_type.lower()
        ingredient_sub_type = ingredient_sub_type.lower()
        unit = unit.lower()


        cur = conn.cursor()
        cur.execute(
            """INSERT INTO "Ingredients"(ingredient_name,ingredient_type,ingredient_sub_type,shelf_life_days,quantity,units,unitprice) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (ingredient_name, ingredient_type, ingredient_sub_type, shelf_life_days, quantity, unit, unitprice))
        conn.commit()
        logger.info(f"Added ingredients to Postgres")
        return {"message": "Ingredient added successfully"}
    except Exception as e:
        # Raise HTTP exception
        logger.exception(f"An Exception Occurred while adding ingredients to Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_ingredient_summary", tags=["seller"])
def get_ingredient_summary():
    """
    Get ingredient summary from Ingredient table of postgres
    :return: ingredient summary
    """
    try:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM "Ingredients" """)
        rows = cur.fetchall()
        # Column Names - id, Created_at,ingredient_name,ingredient_type, ingredient_sub_type, shelf_life_days, quantity, unit
        logger.info(f"Total number of ingredients in the table: {len(rows)}")
        ingredients = []
        for row in rows:
            ingredient = {'name': row[2], 'quantity': row[6], 'unit': row[8], 'shelf_life_days': row[5],
                          'ingredient_type': row[3], 'ingredient_sub_type': row[4], 'ingredient_id': row[0],
                          'unitprice': row[7]}
            ingredients.append(ingredient)
        logger.info(f"Read ingredients from Postgres, Summarizing")

        # Make summary with Vertex AI
        template = """ 
        CONTEXT: You are an AI bot provided with a list of ingredients {ingredients}. You need to sum up , group & summarize the list of ingredients.
        TASK: Group up all Ingredients based on their name and type , sum up their quantity and provide a summary of the ingredients.
        ANSWER: Provide the JSON key-value pairs without special chars ingredient_type1:ingredient_name1:quantity,ingredient_name2:quantity,ingredient_type2:ingredient_name1:quantity,ingredient_name2:quantity. For example: "Vegetables":"Tomato":10,"Potato":20,"Spices":"Salt":10,"Pepper":20
        CONSTRAINTS: Keep in mind the summary should be based on ingredient name and type.
        In case of similar names like Tomato and Tomato Puree, group them together, Add their Quantities, like Potato 500 gram, Potato 500 g, Potato 1kg,Potato  8 kilogram, group all and  sum them up like Potato: 10kg.
        """

        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm

        # Generate the summary
        try:
            s =  chain.invoke({'ingredients': json.dumps(ingredients)})
            return(cleaned(s))

        except Exception as e:
            logger.exception(f"An Exception Occurred while generating summary using Vertex AI --> {e}")
            raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        # Raise HTTP exception
        logger.exception(f"An Exception Occurred while reading ingredients from Postgres --> {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/reengineer_dish", tags=["seller"])
def reengineer_dish(dish_name: str = Form(...), preferred_cuisine: str = Form(...)):
    """
    Reengineer the dish with same ingredients
    :param dish_name:
    :return: New dish name
    """
    template = """ Context: You are a chef of a {preferred_cuisine} restaurant. You are given a dish that you need to reengineer. Please recommend some other dish, that has same ingredients as {dish_name}. You always have flour, water, spices, milk, curd, onion, tomato, ginger, garlic, oil, butter, ghee in your inventory,
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


@router.post("/catalog_image_generator")
def catalog_image_generator(dish_name: str = Form(...), image_type: Optional[str] = Form(None)):
    """
    Generate image for the dish
    :param dish_name:
    :param image_type:
    :return:
    """
    image_type = image_type or "realistic"
    template = """ Context: You are an AI bot responsible for Image generation of dishes in a Restaraunt. 
    TASK: You are given a dish {dish_name}. Please generate a Prompt to generate {image_type}, well-plated, mouth-watering and tempting image for the dish to display the serving suggestions.
    Answer: Provide the Prompt 
    """
    prompt = PromptTemplate.from_template(template)
    chain = LLMChain(prompt=prompt, llm=dalle_llm)
    try:
        image_url = DallEAPIWrapper().run(chain.run({'dish_name': dish_name, 'image_type': image_type}))
        logger.info(f"Image generated successfully")
        return {"image_url": image_url}
    except Exception as e:
        logger.exception(f"An Exception Occurred while generating image using Open AI --> {e}")
        raise HTTPException(status_code=500, detail=str(e))
