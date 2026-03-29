from __future__ import annotations

from typing import Optional

from database.connection import get_connection
from models.linea import Linea


class LineasRepository:
    """
    Repositorio para operaciones CRUD de líneas.
    """

    @staticmethod
    def create(linea: Linea) -> int:
        query = """
            INSERT INTO lineas (
                codigo_linea,
                nombre_linea,
                tonelaje_batch,
                capacidad_tn_hora,
                activo,
                tiempo_limpieza_corta_min,
                tiempo_limpieza_profunda_min,
                tiempo_flush_min,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    linea.codigo_linea,
                    linea.nombre_linea,
                    linea.tonelaje_batch,
                    linea.capacidad_tn_hora,
                    int(linea.activo),
                    linea.tiempo_limpieza_corta_min,
                    linea.tiempo_limpieza_profunda_min,
                    linea.tiempo_flush_min,
                    linea.observaciones,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def get_by_id(id_linea: int) -> Optional[Linea]:
        query = """
            SELECT *
            FROM lineas
            WHERE id_linea = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (id_linea,)).fetchone()

        return Linea.from_row(row) if row else None

    @staticmethod
    def get_by_codigo(codigo_linea: str) -> Optional[Linea]:
        query = """
            SELECT *
            FROM lineas
            WHERE codigo_linea = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (codigo_linea,)).fetchone()

        return Linea.from_row(row) if row else None

    @staticmethod
    def list_all(include_inactive: bool = True) -> list[Linea]:
        query = "SELECT * FROM lineas"
        params: tuple = ()

        if not include_inactive:
            query += " WHERE activo = 1"

        query += " ORDER BY nombre_linea"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [Linea.from_row(row) for row in rows]

    @staticmethod
    def update(linea: Linea) -> bool:
        if linea.id_linea is None:
            raise ValueError("No se puede actualizar una línea sin id_linea.")

        query = """
            UPDATE lineas
            SET
                codigo_linea = ?,
                nombre_linea = ?,
                tonelaje_batch = ?,
                capacidad_tn_hora = ?,
                activo = ?,
                tiempo_limpieza_corta_min = ?,
                tiempo_limpieza_profunda_min = ?,
                tiempo_flush_min = ?,
                observaciones = ?
            WHERE id_linea = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    linea.codigo_linea,
                    linea.nombre_linea,
                    linea.tonelaje_batch,
                    linea.capacidad_tn_hora,
                    int(linea.activo),
                    linea.tiempo_limpieza_corta_min,
                    linea.tiempo_limpieza_profunda_min,
                    linea.tiempo_flush_min,
                    linea.observaciones,
                    linea.id_linea,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(id_linea: int) -> bool:
        query = """
            DELETE FROM lineas
            WHERE id_linea = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_linea,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def deactivate(id_linea: int) -> bool:
        query = """
            UPDATE lineas
            SET activo = 0
            WHERE id_linea = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_linea,))
            conn.commit()
            return cursor.rowcount > 0
