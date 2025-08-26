from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="API de recherche de produits",
    description="API pour rechercher et gérer des produits."
)


class Product(BaseModel):
    name: str = Field(..., example="Pommes", description="Nom du produit.")
    expiration_datetime: datetime = Field(..., example="2025-08-25T10:00:00Z",description="Date et heure d'expiration du produit.")
    price: float = Field(..., example=1.50, description="Prix du produit.")


products_db: List[Product] = [
    Product(name="Pommes", expiration_datetime=datetime(2025, 8, 25, 10, 0, 0), price=1.50),
    Product(name="Bananes", expiration_datetime=datetime(2025, 8, 28, 12, 30, 0), price=2.75),
    Product(name="Lait", expiration_datetime=datetime(2025, 9, 10, 8, 0, 0), price=1.00),
    Product(name="Pain", expiration_datetime=datetime(2025, 8, 26, 15, 0, 0), price=3.50),
    Product(name="Yaourt", expiration_datetime=datetime(2025, 9, 5, 9, 0, 0), price=0.75),
]


@app.get("/products", response_model=List[Product], summary="Rechercher des produits")
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
