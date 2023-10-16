import time

from fastapi import APIRouter
import json
import logging
import requests

from fastapi import Form, HTTPException, Header
from typing import Annotated, Union
from langchain.prompts import PromptTemplate

from ..settings.config import Config
from ..utils.square_payments import get_square_connection
from ..utils.clean import cleaned


# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

config = Config.get_instance()
conn = config.get_postgres_connection()
llm = config.get_vertex_ai_connection()
openai_llm = config.get_openai_text_connection()
openai_llm_chat = config.get_openai_chat_connection()



# Tools for Ingredients and Menu
def read_from_postgres():
    """
    Used to Read from Postgres Table containing Ingredients
    Read Ingredients from Postgres. Information is stored in a list of dictionaries. Each dictionary contains {name, quantity, unit, shelf_life_days, ingredient_type, ingredient_sub_type, unit_price}
    :return: List of Ingredients containing {name, quantity, unit, shelf_life_days, ingredient_type, ingredient_sub_type}
    """
    try:
        ingredients = []
        logger.info(f"Reading from Postgres")
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM "Ingredients" """)
        rows = cur.fetchall()
        logger.info(f"Read from Postgres")
        for row in rows:
            ingredient = {'name': row[2], 'quantity': row[6], 'unit': row[8], 'shelf_life_days': row[5],
                          'ingredient_type': row[3], 'ingredient_sub_type': row[4], 'ingredient_id': row[0],
                          'unitprice': row[7]}
            ingredients.append(ingredient)
        return ingredients
    except Exception as e:
        logger.exception(f"An Exception Occurred while reading from Postgres --> {e}")


def read_menu_from_square_catalog(access_token):
    """
    Used to Read Menu from Square Catalog
    :return:
    """

    #     square_client, square_location_id = get_square_connection(access_token)
    #     result = square_client.catalog.list_catalog(
    #         types="ITEM",  # DEFAULT MENU TYPE IS ITEM
    #     )
    #     if result.is_success():
    #         return result.body
    #     elif result.is_error():
    #         logger.error(f"Error Reading From Catalog{result.errors}")
    # except Exception as e:
    #     logger.exception(f"An Exception Occurred while reading from Square --> {e}")

    url = "https://connect.squareupsandbox.com/v2/catalog/list?types=ITEM"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Read from Square")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in reading from Square -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))



def summary(history):
    """
    Summarize the history of chat
    :param history:
    :return: summarized history
    """
    try:
        logger.info(f"Summarizing history of chat")
        template = """ 
        CONTEXT: You are a AI agent, who is going to read a conversation between a customer and a customer service agent. You need to summarize the conversation keeping all the important points from conversation intact in summary.
        TASK: Summarize the conversation between customer and customer service agent, while maintaining the context and important information of the conversation. 
        ANSWER: Just provide the summary of the conversation in Str Format. For example: "this is a summary of the conversation"
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        history_summary = {"Conversation Summary": chain.invoke(json.dumps(history))}
        logger.info(f"Summarized history of chat")
        return history_summary
    except Exception as e:
        logger.exception(f"An Exception Occurred while summarizing history of chat --> {e}")


@router.post("/chat")
def chat(access_token: Annotated[Union[str, None], Header()], message: str = Form(...), history: list = Form(...)):
    """
    This function will chat with Vertex AI
    :param message:
    :param history:
    :return:
    """
    # use read_from_postgres() as a Agent tool to read Ingredients with Langchain
    # tools = load_tools(tool_names, llm=llm)
    if history is None:
        history = []



    # Chat with Vertex AI
    # Need Buffer size check on history (Summarization may help)
    # Use tools for Ingredients and Menu

    ingredients = read_from_postgres()
    menu = read_menu_from_square_catalog(access_token)

    if "PAYMENT" in message or "Payment" in message or "payment" in message or "Pay" in message or "pay" in message:
        return {"response": "Please pay for your order", "history": history, "stop": True, "payment": True}

    if "STOP" in message or "Stop" in message or "stop" in message:
        return {"response": "STOPPING CHAT ", "history": history, "stop": True, "payment": False}

    else:

        template = """ Context: You are a customer service agent for a restaurant. You are chatting with a customer who wants to order food. Here is the history of chat you had with the customer: {history}, now the customer is saying {message}. Please respond to the customer in poliet manner. In case there is no history of chat, just respond to the customer current message.
        Task: Take Customer Order
        Order: Ask Customer for Dish from Menu, Serve Size, Customization for all orders
        Answer: Just provide the response to the customer. For example: Hi, I am sorry for the inconvenience. I will check with the chef and get back to you.
        Menu includes {menu} along with dish price
        Ingredients for customization include {ingredients} 
        Not in Menu: If Customer asks for something not in Menu, say that it is not available.
        Customization: You can customize the menu as per customer requirement, keeping in Mind the Ingredients. For example: I want to order a pizza with extra cheese and no onion. 
        No Customization: If no customization is possible due to lack of Ingredients, just say that customization is not possible.
        Stop: Once Customer is done ordering, and you have confirmed the order .You can stop the chat by summarizing the order and saying: Thank you for your order. Your order will be delivered in few minutes. Have a nice day.
        STOP EXAMPLE: "STOPPING CHAT - Thank you for your order. Your order will be delivered in few minutes. Have a nice day."
        Continue: If Customer wants to order more, you can continue the chat by saying: What else would you like to order?
        Constraints: You can only use Ingredients available in the restaurant for customization. Customer can only order from Menu. Customer can only order one serve size at a time. 
        PRICING: Once a customer is done customising and finalizing the dish, estimate the price, based on Menu provided, serve size and quantity. Do not consider Individual Ingredient Price.
        Pricing Formula: Price = Dish Price * serve size * quantity so if unit price of pizza is 10$, 3 small pizza will be 10*3*1 = 30$, Large pizza is equivalent to 2 small pizza, so 1 large pizza will be 10*2*1 = 20$.
        EXAMPLE: If a customer orders a pizza with extra cheese and no onion, you can say: Your order will cost you 10$.
        RESPONSE CONSTRAINT: DONT OUTPUT HISTORY OF CHAT, JUST OUTPUT RESPONSE TO CUSTOMER.
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | openai_llm_chat

        try:
            response = str(chain.invoke(
                {"message": str(message), "history": str("".join(history)), "menu": json.dumps(menu),
                 "ingredients": json.dumps(ingredients)}))
            if "STOPPING CHAT" in response or "Stopping Chat" in response or "stopping chat" in response or "Stopping chat" in response or "stop chat" in response or "Stop chat" in response or "STOP CHAT" in response:
                history.append({"Customer": message, "Agent": response})
                return {"response": response, "history": history, "stop": True, "payment": True}
            else:
                history.append({"Customer": message, "Agent": response})
                return {"response": response, "history": history, "stop": False, "payment": False}

        except Exception as e:
            logger.exception(f"An Exception Occurred while chatting with Vertex AI --> {e}")
            response = "I am sorry, I am not able to understand you. Please try again."
            raise HTTPException(status_code=500, detail=f"An Exception Occurred while chatting with Vertex AI --> {e}")
            return {"response": response, "history": history, "stop": True, "payment": False}


@router.post("/order_summarization")
def order_summarization(history: str = Form(...)):
    """
    This function will summarize the order and redirect to Square Payment API
    :param history:
    :return: order summary
    """
    if not history:
        raise HTTPException(status_code=500, detail=f"Order History is Empty")
    else:

        template = """
        CONTEXT: You are a AI agent, who is going to read a conversation between a customer and a customer service agent regarding order at a restaurant {history}. You need to summarize the order keeping all the important points regdarding order, serve, quantity, Customizations and price of dish from conversation intact in summary.
        TASK: Summarize the order from the conversation between customer and customer service agent, while maintaining the context and important information regdarding order, serve, quantity, Customizations and pricing of the conversation.
        ANSWER: Just provide the summary of the order in JSON, key-value pairs without special chars  Format. If there is no customization, use None, if there is a dish but no serve, use Medium and if there is no Quantity, use 1, if there is no price use 5. Currency is always "CAD"
         For example: 
         ("order":[("name": "Aalo prantha","quantity": "1", "base_price_money": ( "amount": 20,"currency": "CAD"),
                   ("name": "Pizza","quantity": "2", "base_price_money": ( "amount": 30,"currency": "CAD"),]
        )
        
            
        JUST OUTPUT ORDER SUMMARY IN JSON FORMAT, only Key-value pairs without special chars and spaces
        """

        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        try:
            order_summary = chain.invoke({"history":history})
            try:
                order_summary = json.loads(cleaned(order_summary))
            except:
                order_summary = cleaned(order_summary)
        except Exception as e:
            logger.exception(f"An Exception Occurred while summarizing order --> {e}")
            raise HTTPException(status_code=500, detail=f"An Exception Occurred while summarizing order --> {e}")

        return order_summary


@router.post("/get_customers")
def get_customers(access_token: Annotated[Union[str, None], Header()], customer_id: str = Form(...)):
    """
    This function will get customer details from Square
    :param customer_id:
    :return: customer details
    """
    url = f"https://connect.squareupsandbox.com/v2/customers/{customer_id}"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info(f"Read from Square")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in reading from Square -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))

@router.post("/list_customers")
def list_customers(access_token: Annotated[Union[str, None], Header()]):
    """
    This function will list all customers from Square
    :param customer_id:
    :return: customer details
    """
    url = "https://connect.squareupsandbox.com/v2/customers"
    headers = {
        "Square-Version": "2023-09-25",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    print(response)

    if response.status_code == 200:
        logger.info(f"Read from Square")
        return response.json()
    elif response.status_code == 400:
        logger.error(f"Error in reading from Square -->    {response.json()}")
        raise HTTPException(status_code=500, detail=str(response.json()))