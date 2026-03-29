from __future__ import annotations

from typing import Optional

from database.connection import get_connection
from models.regla_riesgo import ReglaRiesgo


class ReglasRepository:
    """
    Repositorio para operaciones CRUD de reglas de riesgo.
    """

    @staticmethod
    def create(regla: ReglaRiesgo) -> int:
        query = """
            INSERT INTO reglas_riesgo (
                categoria_origen,
                categoria_destino,
                accion,
                id_limpieza,
                prioridad,
                activo,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    regla.categoria_origen,
                    regla.categoria_destino,
                    regla.accion,
                    regla.id_limpieza,
                    regla.prioridad,
                    int(regla.activo),
                    regla.observaciones,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def get_by_id(id_regla: int) -> Optional[ReglaRiesgo]:
        query = """
            SELECT *
            FROM reglas_riesgo
            WHERE id_regla = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (id_regla,)).fetchone()

        return ReglaRiesgo.from_row(row) if row else None

    @staticmethod
    def list_all(include_inactive: bool = True) -> list[ReglaRiesgo]:
        query = "SELECT * FROM reglas_riesgo"
        params: tuple = ()

        if not include_inactive:
            query += " WHERE activo = 1"

        query += """
            ORDER BY categoria_origen, categoria_destino, prioridad
        """

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [ReglaRiesgo.from_row(row) for row in rows]

    @staticmethod
    def get_rule(
        categoria_origen: str,
        categoria_destino: str,
        include_inactive: bool = False,
    ) -> list[ReglaRiesgo]:
        query = """
            SELECT *
            FROM reglas_riesgo
            WHERE categoria_origen = ?
              AND categoria_destino = ?
        """
        params: list = [categoria_origen, categoria_destino]

        if not include_inactive:
            query += " AND activo = 1"

        query += " ORDER BY prioridad"

        with get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()

        return [ReglaRiesgo.from_row(row) for row in rows]

    @staticmethod
    def update(regla: ReglaRiesgo) -> bool:
        if regla.id_regla is None:
            raise ValueError("No se puede actualizar una regla sin id_regla.")

        query = """
            UPDATE reglas_riesgo
            SET
                categoria_origen = ?,
                categoria_destino = ?,
                accion = ?,
                id_limpieza = ?,
                prioridad = ?,
                activo = ?,
                observaciones = ?
            WHERE id_regla = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    regla.categoria_origen,
                    regla.categoria_destino,
                    regla.accion,
                    regla.id_limpieza,
                    regla.prioridad,
                    int(regla.activo),
                    regla.observaciones,
                    regla.id_regla,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(id_regla: int) -> bool:
        query = """
            DELETE FROM reglas_riesgo
            WHERE id_regla = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_regla,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def deactivate(id_regla: int) -> bool:
        query = """
            UPDATE reglas_riesgo
            SET activo = 0
            WHERE id_regla = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_regla,))
            conn.commit()
            return cursor.rowcount > 0
