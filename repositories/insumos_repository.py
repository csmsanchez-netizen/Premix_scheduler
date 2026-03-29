from __future__ import annotations

from typing import Optional

from database.connection import get_connection
from models.insumo import Insumo


class InsumosRepository:
    """
    Repositorio para operaciones CRUD de insumos.
    """

    @staticmethod
    def create(insumo: Insumo) -> int:
        query = """
            INSERT INTO insumos (
                codigo_insumo,
                nombre_insumo,
                categoria_riesgo,
                nivel_riesgo,
                activo,
                limpieza_sugerida,
                es_critico,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    insumo.codigo_insumo,
                    insumo.nombre_insumo,
                    insumo.categoria_riesgo,
                    insumo.nivel_riesgo,
                    int(insumo.activo),
                    insumo.limpieza_sugerida,
                    int(insumo.es_critico),
                    insumo.observaciones,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def get_by_id(id_insumo: int) -> Optional[Insumo]:
        query = """
            SELECT *
            FROM insumos
            WHERE id_insumo = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (id_insumo,)).fetchone()

        return Insumo.from_row(row) if row else None

    @staticmethod
    def get_by_codigo(codigo_insumo: str) -> Optional[Insumo]:
        query = """
            SELECT *
            FROM insumos
            WHERE codigo_insumo = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (codigo_insumo,)).fetchone()

        return Insumo.from_row(row) if row else None

    @staticmethod
    def list_all(include_inactive: bool = True) -> list[Insumo]:
        query = "SELECT * FROM insumos"
        params: tuple = ()

        if not include_inactive:
            query += " WHERE activo = 1"

        query += " ORDER BY nombre_insumo"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [Insumo.from_row(row) for row in rows]

    @staticmethod
    def update(insumo: Insumo) -> bool:
        if insumo.id_insumo is None:
            raise ValueError("No se puede actualizar un insumo sin id_insumo.")

        query = """
            UPDATE insumos
            SET
                codigo_insumo = ?,
                nombre_insumo = ?,
                categoria_riesgo = ?,
                nivel_riesgo = ?,
                activo = ?,
                limpieza_sugerida = ?,
                es_critico = ?,
                observaciones = ?
            WHERE id_insumo = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    insumo.codigo_insumo,
                    insumo.nombre_insumo,
                    insumo.categoria_riesgo,
                    insumo.nivel_riesgo,
                    int(insumo.activo),
                    insumo.limpieza_sugerida,
                    int(insumo.es_critico),
                    insumo.observaciones,
                    insumo.id_insumo,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(id_insumo: int) -> bool:
        query = """
            DELETE FROM insumos
            WHERE id_insumo = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_insumo,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def deactivate(id_insumo: int) -> bool:
        query = """
            UPDATE insumos
            SET activo = 0
            WHERE id_insumo = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_insumo,))
            conn.commit()
            return cursor.rowcount > 0
