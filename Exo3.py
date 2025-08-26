from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict

app = FastAPI(
    title="API de gestion de tâches",
    description="API pour créer, lire, mettre à jour et supprimer des tâches."
)


class Task(BaseModel):
    id: int = Field(..., example=1, description="Identifiant unique de la tâche.")
    title: str = Field(..., example="Faire les courses", description="Titre de la tâche.")
    completed: bool = Field(..., example=False, description="Statut d'achèvement de la tâche.")


tasks_db: Dict[int, Task] = {
    1: Task(id=1, title="Apprendre FastAPI", completed=False),
    2: Task(id=2, title="Faire du sport", completed=True),
}

next_id = 3


@app.get("/tasks", response_model=List[Task], summary="Récupérer toutes les tâches")
async def get_all_tasks():
    """
    Retourne la liste de toutes les tâches.
    """
    return list(tasks_db.values())


@app.post("/tasks", response_model=List[Task], status_code=201, summary="Créer de nouvelles tâches")
async def create_tasks(new_tasks: List[Task] = Body(...)):

    global next_id
    created_tasks = []
    for task in new_tasks:
        if task.id in tasks_db:
            raise HTTPException(status_code=400, detail=f"La tâche avec l'ID {task.id} existe déjà.")

        tasks_db[task.id] = task
        created_tasks.append(task)
    return created_tasks


@app.get("/tasks/{id}", response_model=Task, summary="Récupérer une tâche par ID")
async def get_task_by_id(id: int):

    task = tasks_db.get(id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{id}", response_model=Task, summary="Supprimer une tâche par ID")
async def delete_task_by_id(id: int):

    if id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    deleted_task = tasks_db.pop(id)
    return deleted_task


@app.delete("/tasks", response_model=List[Task], summary="Supprimer une liste de tâches par ID")
async def delete_tasks(ids: List[int] = Body(..., example=[1, 2])):

    deleted_tasks = []
    for task_id in ids:
        if task_id in tasks_db:
            deleted_task = tasks_db.pop(task_id)
            deleted_tasks.append(deleted_task)

    return deleted_tasks
