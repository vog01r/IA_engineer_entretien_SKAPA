import uvicorn

from app.db.crud import create_tables

if __name__ == "__main__":
    create_tables()
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
