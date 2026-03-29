from __future__ import annotations

from typing import Optional

from database.connection import get_connection
from models.orden_produccion import OrdenProduccion


class OrdenesRepository:
    """
    Repositorio para operaciones CRUD de órdenes de producción.
    """

    @staticmethod
    def create(orden: OrdenProduccion) -> int:
        query = """
            INSERT INTO ordenes_produccion (
                numero_op,
                fecha_op,
                id_formula,
                toneladas,
                prioridad,
                fecha_compromiso,
                id_linea_preferida,
                estado,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    orden.numero_op,
                    orden.fecha_op,
                    orden.id_formula,
                    orden.toneladas,
                    orden.prioridad,
                    orden.fecha_compromiso,
                    orden.id_linea_preferida,
                    orden.estado,
                    orden.observaciones,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def get_by_id(id_op: int) -> Optional[OrdenProduccion]:
        query = """
            SELECT *
            FROM ordenes_produccion
            WHERE id_op = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (id_op,)).fetchone()

        return OrdenProduccion.from_row(row) if row else None

    @staticmethod
    def get_by_numero(numero_op: str) -> Optional[OrdenProduccion]:
        query = """
            SELECT *
            FROM ordenes_produccion
            WHERE numero_op = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (numero_op,)).fetchone()

        return OrdenProduccion.from_row(row) if row else None

    @staticmethod
    def list_all(include_cancelled: bool = True) -> list[OrdenProduccion]:
        query = "SELECT * FROM ordenes_produccion"
        params: tuple = ()

        if not include_cancelled:
            query += " WHERE estado != 'CANCELADA'"

        query += " ORDER BY fecha_op, prioridad DESC, numero_op"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [OrdenProduccion.from_row(row) for row in rows]

    @staticmethod
    def list_pendientes() -> list[OrdenProduccion]:
        query = """
            SELECT *
            FROM ordenes_produccion
            WHERE estado = 'PENDIENTE'
            ORDER BY fecha_op, prioridad DESC, numero_op
        """

        with get_connection() as conn:
            rows = conn.execute(query).fetchall()

        return [OrdenProduccion.from_row(row) for row in rows]

    @staticmethod
    def update(orden: OrdenProduccion) -> bool:
        if orden.id_op is None:
            raise ValueError("No se puede actualizar una orden sin id_op.")

        query = """
            UPDATE ordenes_produccion
            SET
                numero_op = ?,
                fecha_op = ?,
                id_formula = ?,
                toneladas = ?,
                prioridad = ?,
                fecha_compromiso = ?,
                id_linea_preferida = ?,
                estado = ?,
                observaciones = ?
            WHERE id_op = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    orden.numero_op,
                    orden.fecha_op,
                    orden.id_formula,
                    orden.toneladas,
                    orden.prioridad,
                    orden.fecha_compromiso,
                    orden.id_linea_preferida,
                    orden.estado,
                    orden.observaciones,
                    orden.id_op,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def update_estado(id_op: int, nuevo_estado: str) -> bool:
        query = """
            UPDATE ordenes_produccion
            SET estado = ?
            WHERE id_op = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (nuevo_estado, id_op))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(id_op: int) -> bool:
        query = """
            DELETE FROM ordenes_produccion
            WHERE id_op = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_op,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def cancel(id_op: int) -> bool:
        query = """
            UPDATE ordenes_produccion
            SET estado = 'CANCELADA'
            WHERE id_op = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_op,))
            conn.commit()
            return cursor.rowcount > 0
