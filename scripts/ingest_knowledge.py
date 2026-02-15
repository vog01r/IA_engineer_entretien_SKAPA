#!/usr/bin/env python3
"""Script d'ingestion de la base de connaissances pour l'agent RAG."""

import sys
from pathlib import Path

# Ajouter la racine au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.crud import create_tables, insert_chunk

# data/ = documents et contenus (séparé du code)
KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"


def ingest_document(filepath: Path) -> int:
    """Ingère un fichier texte dans la base (chunks par paragraphe)."""
    content = filepath.read_text(encoding="utf-8")
    chunks = [c.strip() for c in content.split("\n\n") if c.strip() and len(c.strip()) > 30]
    for i, chunk in enumerate(chunks):
        insert_chunk(str(filepath.name), chunk, chunk_index=i)
    return len(chunks)


def main():
    create_tables()
    total = 0
    for f in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        n = ingest_document(f)
        total += n
        print(f"  {f.name}: {n} chunks")
    print(f"Ingestion terminée : {total} chunks au total.")


if __name__ == "__main__":
    main()
