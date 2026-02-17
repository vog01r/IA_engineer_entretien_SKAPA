web: sh -c 'python -c "from backend.shared.db.crud import create_tables; create_tables()" && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}'
