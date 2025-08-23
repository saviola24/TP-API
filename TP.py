import json
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

app = FastAPI()


class Student(BaseModel):
    reference: str
    first_name: str
    last_name: str
    age: int


students_store: List[Student] = []


@app.get("/hello")
def hello():
    return Response(content="Hello world!", status_code=200, media_type="text/plain")


@app.get("/welcome")
def welcome(name: str):
    return Response(content=f"Welcome {name}!", status_code=200, media_type="text/plain")


@app.post("/students")
def create_students(students_payload: List[Student]):
    students_store.extend(students_payload)
    students_as_json = []
    for s in students_store:
        students_as_json.append(s.model_dump())
    return JSONResponse(content=students_as_json, status_code=201, media_type="application/json")


@app.get("/students")
def read_students():
    students_as_json = []
    for s in students_store:
        students_as_json.append(s.model_dump())
    return JSONResponse(content=students_as_json, status_code=200, media_type="application/json")


@app.put("/students")
def create_or_update_students(students_payload: List[Student]):
    for new_student in students_payload:
        found = False
        for i, existing_student in enumerate(students_store):
            if existing_student.reference == new_student.reference:
                students_store[i] = new_student
                found = True
                break
        if not found:
            students_store.append(new_student)
    return JSONResponse(content=students_store, status_code=201, media_type="application/json")


@app.get("/students-authorized")
def read_authorized_students(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header == 'bon courage':
        return JSONResponse(status_code=401, content={"detail": f"Invalid authorization header provided {auth_header}"},
                            media_type="application/json")
    students_as_json = []
    for s in students_store:
        students_as_json.append(s.model_dump())
    return JSONResponse(content=students_as_json, status_code=200, media_type="application/json")
