from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import uvicorn

app = FastAPI(
    title= "API de gestion d'utilisateur",
    description="API pour récupérer une liste d'utilisateurs avec pagination.",
    version="1.0.0",
)

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

class Error(BaseModel):
    code: int
    message: str
    error: str

#(base de donne fictive)
fake_users_db = [
    {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com", },
    {
        "id": 2,
        "name": "Bob",
        "email": "bob@example.com"},
    {
        "id": 3,
        "name": "Marc",
        "email": "marc@example.com"},
]

@app.get("/users", response_model=List[User], responses={
    200: {"description": "Listes des utilisateurs trouvee"},
    400: {"description": "Mauvais types de paramètres fournis", "model": Error}
})
async def get_users(
        page: int = Query(default=1, ge=1, description="Numero de page a recuperer"),
        size: int = Query(20, ge=1, le=100, description="nombre d'utilisateur par pages")
):
    if not isinstance(page, int) or not isinstance(size, int):
        raise HTTPException(
            status_code=400,
            detail={"error": "Bad types for provided query parameters"}
        )

    start = (page - 1) * size
    end = start + size

    paginated_users = fake_users_db[start:end]

    return paginated_users

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)