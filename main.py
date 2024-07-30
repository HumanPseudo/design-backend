from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, init_db
from models import Todo as TodoModel
from schemas import Todo as TodoSchema, TodoCreate, TodoUpdate

app = FastAPI()

# Initialize the database
init_db()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todos/", response_model=TodoSchema)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """
    Create a new To-Do item.

    - **todo**: A `TodoCreate` object with the title, description (optional), and completion status (optional).
    - **db**: The database session dependency.

    Returns the created To-Do item with its unique ID.
    """
    db_todo = TodoModel(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[TodoSchema])
def read_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve a list of all To-Do items.

    - **skip**: Number of items to skip (default: 0).
    - **limit**: Maximum number of items to return (default: 10).
    - **db**: The database session dependency.

    Returns a list of To-Do items.
    """
    todos = db.query(TodoModel).offset(skip).limit(limit).all()
    return todos

@app.get("/todos/{todo_id}", response_model=TodoSchema)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single To-Do item by its ID.

    - **todo_id**: The unique identifier of the To-Do item.
    - **db**: The database session dependency.

    Returns the To-Do item with the specified ID.
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    """
    Update an existing To-Do item.

    - **todo_id**: The unique identifier of the To-Do item to update.
    - **todo**: A `TodoUpdate` object with the new title, description (optional), and completion status (optional).
    - **db**: The database session dependency.

    Returns the updated To-Do item.
    """
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", response_model=TodoSchema)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    Delete a To-Do item by its ID.

    - **todo_id**: The unique identifier of the To-Do item to delete.
    - **db**: The database session dependency.

    Returns the deleted To-Do item.
    """
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return db_todo
