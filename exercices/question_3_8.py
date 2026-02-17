#!/usr/bin/env python3
"""
Question 3.8 — Script d'analyse de la base de connaissances (3.11 + 3.12)

Script standalone : python exercices/question_3_8.py (depuis la racine du projet)

Affiche :
1. Nombre total de chunks par document source (source_file)
2. Nombre moyen de caractères par chunk
3. Les 3 chunks les plus courts (potentiellement inutiles / à nettoyer)
4. Nombre d'enregistrements dont created_at est vide ou NULL
5. Pour chaque table : nombre d'enregistrements dont updated_date est vide ou NULL
"""

import sqlite3
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database.db"


def get_connection():
    """Ouvre une connexion SQLite. Lève une exception si le fichier est absent."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Fichier base de données introuvable : {DATABASE_PATH}\n"
            "Lancez l'application au moins une fois pour créer database.db"
        )
    return sqlite3.connect(DATABASE_PATH)


def count_chunks_by_source(conn) -> list[tuple[str, int]]:
    """Retourne le nombre de chunks par source_file (GROUP BY + COUNT)."""
    cursor = conn.execute(
        """
        SELECT source_file, COUNT(*) AS nb_chunks
        FROM knowledge_chunks
        GROUP BY source_file
        ORDER BY nb_chunks DESC
        """
    )
    return cursor.fetchall()


def average_characters_per_chunk(conn) -> float | None:
    """Retourne le nombre moyen de caractères par chunk (AVG + LENGTH)."""
    cursor = conn.execute(
        "SELECT AVG(LENGTH(content)) AS avg_length FROM knowledge_chunks"
    )
    row = cursor.fetchone()
    return row[0] if row and row[0] is not None else None


def get_shortest_chunks(conn, limit: int = 3) -> list[tuple[int, str, str, int]]:
    """Retourne les N chunks les plus courts (ORDER BY LENGTH, LIMIT)."""
    cursor = conn.execute(
        """
        SELECT id, source_file, content, LENGTH(content) AS len_content
        FROM knowledge_chunks
        ORDER BY LENGTH(content) ASC
        LIMIT ?
        """,
        (limit,),
    )
    return cursor.fetchall()


def count_missing_created_at(conn) -> int:
    """Compte les enregistrements où created_at est NULL ou vide."""
    cursor = conn.execute(
        """
        SELECT COUNT(*) FROM knowledge_chunks
        WHERE created_at IS NULL
           OR TRIM(created_at) = ''
        """
    )
    return cursor.fetchone()[0]


def ensure_table_exists(conn, table: str) -> bool:
    """Vérifie que la table existe."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    )
    return cursor.fetchone() is not None


def truncate_content(content: str, max_length: int = 80) -> str:
    """Tronque le contenu pour l'affichage, avec ellipsis si nécessaire."""
    content = content.strip()
    if len(content) <= max_length:
        return content
    return content[: max_length - 3].rstrip() + "..."


# ─── 3.12 : updated_date par table ──────────────────────────────────────────

def get_tables(conn) -> list[str]:
    """Retourne la liste des tables (hors schéma interne SQLite)."""
    cursor = conn.execute(
        """
        SELECT name FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in cursor.fetchall()]


def table_has_column(conn, table: str, column: str) -> bool:
    """Vérifie si la table possède la colonne spécifiée."""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def count_empty_or_null_updated_date(conn, table: str) -> int | None:
    """
    Compte les enregistrements où updated_date est NULL ou vide.
    Retourne None si la colonne n'existe pas.
    """
    if not table_has_column(conn, table, "updated_date"):
        return None

    cursor = conn.execute(
        f"""
        SELECT COUNT(*) FROM "{table}"
        WHERE updated_date IS NULL
           OR TRIM(updated_date) = ''
        """
    )
    return cursor.fetchone()[0]


def print_updated_date_report(conn) -> None:
    """Affiche le rapport updated_date vide/NULL par table."""
    tables = get_tables(conn)
    if not tables:
        return

    print("=" * 60)
    print("5. Enregistrements avec updated_date vide ou NULL (par table)")
    print("=" * 60)

    for table in tables:
        count = count_empty_or_null_updated_date(conn, table)
        if count is None:
            print(f"  • {table}: colonne updated_date absente")
        else:
            print(f"  • {table}: {count}")
    print()


def main() -> int:
    """Point d'entrée principal."""
    try:
        conn = get_connection()
    except FileNotFoundError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    try:
        # ─── 3.11 : stats knowledge_chunks ───────────────────────────────────

        if not ensure_table_exists(conn, "knowledge_chunks"):
            print("Erreur : la table 'knowledge_chunks' n'existe pas.", file=sys.stderr)
            print_updated_date_report(conn)
            return 1

        chunks_by_source = count_chunks_by_source(conn)
        total_chunks = sum(n for _, n in chunks_by_source)

        if total_chunks == 0:
            print("La table knowledge_chunks est vide. Aucune donnée à afficher.")
            print()
        else:
            print("=" * 60)
            print("1. Nombre total de chunks par document source")
            print("=" * 60)
            for source_file, count in chunks_by_source:
                print(f"  • {source_file}: {count} chunk(s)")
            print()

            avg_chars = average_characters_per_chunk(conn)
            print("=" * 60)
            print("2. Nombre moyen de caractères par chunk")
            print("=" * 60)
            print(f"  Moyenne : {avg_chars:.1f} caractères" if avg_chars else "  N/A")
            print()

            shortest = get_shortest_chunks(conn, limit=3)
            print("=" * 60)
            print("3. Les 3 chunks les plus courts (potentiellement à nettoyer)")
            print("=" * 60)
            for chunk_id, source_file, content, length in shortest:
                preview = truncate_content(content)
                print(f"  [id={chunk_id}] {source_file} ({length} car.) : « {preview} »")
            print()

            missing_created_at = count_missing_created_at(conn)
            print("=" * 60)
            print("4. Enregistrements avec created_at vide ou NULL")
            print("=" * 60)
            print(f"  Nombre : {missing_created_at}")
            print()

        # ─── 3.12 : updated_date par table (toujours exécuté) ─────────────────

        print_updated_date_report(conn)

        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
