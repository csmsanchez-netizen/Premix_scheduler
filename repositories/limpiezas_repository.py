from __future__ import annotations

from typing import Optional

from database.connection import get_connection
from models.limpieza import Limpieza


class LimpiezasRepository:
    """
    Repositorio para operaciones CRUD de tipos de limpieza.
    """

    @staticmethod
    def create(limpieza: Limpieza) -> int:
        query = """
            INSERT INTO tipos_limpieza (
                codigo_limpieza,
                nombre_limpieza,
                duracion_min,
                activo,
                descripcion
            )
            VALUES (?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    limpieza.codigo_limpieza,
                    limpieza.nombre_limpieza,
                    limpieza.duracion_min,
                    int(limpieza.activo),
                    limpieza.descripcion,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def get_by_id(id_limpieza: int) -> Optional[Limpieza]:
        query = """
            SELECT *
            FROM tipos_limpieza
            WHERE id_limpieza = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (id_limpieza,)).fetchone()

        return Limpieza.from_row(row) if row else None

    @staticmethod
    def get_by_codigo(codigo_limpieza: str) -> Optional[Limpieza]:
        query = """
            SELECT *
            FROM tipos_limpieza
            WHERE codigo_limpieza = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (codigo_limpieza,)).fetchone()

        return Limpieza.from_row(row) if row else None

    @staticmethod
    def list_all(include_inactive: bool = True) -> list[Limpieza]:
        query = "SELECT * FROM tipos_limpieza"
        params: tuple = ()

        if not include_inactive:
            query += " WHERE activo = 1"

        query += " ORDER BY nombre_limpieza"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [Limpieza.from_row(row) for row in rows]

    @staticmethod
    def update(limpieza: Limpieza) -> bool:
        if limpieza.id_limpieza is None:
            raise ValueError("No se puede actualizar una limpieza sin id_limpieza.")

        query = """
            UPDATE tipos_limpieza
            SET
                codigo_limpieza = ?,
                nombre_limpieza = ?,
                duracion_min = ?,
                activo = ?,
                descripcion = ?
            WHERE id_limpieza = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    limpieza.codigo_limpieza,
                    limpieza.nombre_limpieza,
                    limpieza.duracion_min,
                    int(limpieza.activo),
                    limpieza.descripcion,
                    limpieza.id_limpieza,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(id_limpieza: int) -> bool:
        query = """
            DELETE FROM tipos_limpieza
            WHERE id_limpieza = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_limpieza,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def deactivate(id_limpieza: int) -> bool:
        query = """
            UPDATE tipos_limpieza
            SET activo = 0
            WHERE id_limpieza = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_limpieza,))
            conn.commit()
            return cursor.rowcount > 0
