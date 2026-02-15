import os

import uvicorn

from app.db.crud import create_tables

if __name__ == "__main__":
    create_tables()
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.app:app", host="0.0.0.0", port=port, reload=True)
