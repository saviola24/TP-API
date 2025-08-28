from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import secrets

tags_metadata = [
    {"name": "Products", "description": "Opérations liées aux produits."},
    {"name": "Orders", "description": "Opérations liées aux commandes, y compris la création sécurisée."},
]

app = FastAPI(
    title="API de gestion de produits et commandes",
    description="API pour la recherche de produits et la gestion des commandes, avec authentification pour la création de commandes.",
    openapi_tags=tags_metadata
)


class Product(BaseModel):
    name: str = Field(..., example="Pommes", description="Nom du produit.")
    expiration_datetime: datetime = Field(..., example="2025-08-25T10:00:00Z",description="Date et heure d'expiration du produit.")
    price: float = Field(..., example=1.50, description="Prix du produit.")


class Order(BaseModel):
    identifier: int = Field(..., example=101, description="Identifiant unique de la commande.")
    customer_name: str = Field(..., example="Jean Dupont", description="Nom du client.")
    creation_datetime: datetime = Field(..., example="2025-08-25T15:00:00Z",description="Date et heure de création de la commande.")
    total_amount: float = Field(..., example=45.99, description="Montant total de la commande.")


class NewOrderRequest(BaseModel):
    customer_name: str = Field(..., example="Nouvel client", description="Nom du client.")
    total_amount: float = Field(..., example=75.00, description="Montant total.")


products_db: List[Product] = [
    Product(name="Pommes", expiration_datetime=datetime(2025, 8, 25, 10, 0, 0), price=1.50),
    Product(name="Bananes", expiration_datetime=datetime(2025, 8, 28, 12, 30, 0), price=2.75),
    Product(name="Lait", expiration_datetime=datetime(2025, 9, 10, 8, 0, 0), price=1.00),
    Product(name="Pain", expiration_datetime=datetime(2025, 8, 26, 15, 0, 0), price=3.50),
    Product(name="Yaourt", expiration_datetime=datetime(2025, 9, 5, 9, 0, 0), price=0.75),
]

orders_db: Dict[int, Order] = {
    101: Order(identifier=101, customer_name="Jean Dupont", creation_datetime=datetime(2025, 8, 25, 15, 0, 0),
               total_amount=45.99),
    102: Order(identifier=102, customer_name="Marie Curie", creation_datetime=datetime(2025, 8, 26, 9, 0, 0),
               total_amount=120.50),
    103: Order(identifier=103, customer_name="Albert Einstein", creation_datetime=datetime(2025, 8, 26, 10, 0, 0),
               total_amount=80.25),
}

next_order_id = 104

security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/products", response_model=List[Product], tags=["Products"], summary="Rechercher des produits")
async def search_products(
        limit: Optional[int] = Query(None, description="Nombre maximum d'éléments à retourner."),
        q: Optional[str] = Query(None, description="Terme de recherche pour filtrer les produits par nom.")
):
    filtered_products = products_db
    if q:
        filtered_products = [
            product for product in products_db if q.lower() in product.name.lower()
        ]

    if limit is not None:
        return filtered_products[:limit]

    return filtered_products


@app.get("/orders", response_model=List[Order], tags=["Orders"], summary="Obtenir la liste paginée des commandes")
async def get_orders(
        page: int = Query(1, ge=1, description="Numéro de la page à retourner."),
        size: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page.")
):
    all_orders = list(orders_db.values())
    start_index = (page - 1) * size
    end_index = start_index + size
    return all_orders[start_index:end_index]


@app.post("/orders", response_model=Order, status_code=201, tags=["Orders"], summary="Créer une nouvelle commande")
async def create_order(
        new_order: NewOrderRequest,
        username: str = Depends(get_current_user)
):
    global next_order_id
    identifier = next_order_id
    next_order_id += 1

    order = Order(
        identifier=identifier,
        customer_name=new_order.customer_name,
        creation_datetime=datetime.now(),
        total_amount=new_order.total_amount
    )
    orders_db[identifier] = order

    return order
