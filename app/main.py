import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import seller, customer, payments, catalog, ingredient, invoice, order


# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI(
    title="Google AI Square Hackathon",
    description="API for Google AI Square Hackathon",
    version="1",
    openapi_url="/openapi.json",
    docs_url="/",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(seller.router, prefix="/seller", tags=["seller"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(customer.router, prefix="/customer", tags=["customer"])
app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
app.include_router(ingredient.router, prefix="/ingredients", tags=["ingredients"])
app.include_router(invoice.router, prefix="/invoice", tags=["invoice"])
app.include_router(order.router, prefix="/order", tags=["order"])

