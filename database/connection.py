from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from config.settings import DB_PATH, SCHEMA_PATH, ensure_directories


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Retorna una conexión SQLite con foreign keys activadas.
    """
    target_path = db_path or DB_PATH

    try:
        ensure_directories()
        conn = sqlite3.connect(target_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as exc:
        raise RuntimeError(f"Error al abrir la base de datos: {exc}") from exc


def execute_schema(
    schema_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
) -> None:
    """
    Ejecuta el archivo schema.sql para crear tablas e índices.
    """
    target_schema = schema_path or SCHEMA_PATH
    target_db = db_path or DB_PATH

    if not target_schema.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo schema.sql en: {target_schema}"
        )

    try:
        sql_script = target_schema.read_text(encoding="utf-8")

        with get_connection(target_db) as conn:
            conn.executescript(sql_script)
            conn.commit()

    except sqlite3.Error as exc:
        raise RuntimeError(f"Error al ejecutar schema.sql: {exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"Error al leer schema.sql: {exc}") from exc


def initialize_database() -> None:
    """
    Inicializa la base de datos del proyecto.
    """
    try:
        ensure_directories()
        execute_schema()
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo inicializar la base de datos: {exc}"
        ) from exc


def test_connection() -> bool:
    """
    Verifica si la conexión a SQLite funciona.
    """
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1;")
        return True
    except Exception:
        return False
