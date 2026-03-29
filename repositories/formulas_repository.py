from __future__ import annotations

from typing import Optional

from database.connection import get_connection
from models.formula import Formula
from models.formula_detalle import FormulaDetalle


class FormulasRepository:
    """
    Repositorio para operaciones CRUD de fórmulas y su detalle.
    """

    @staticmethod
    def create(formula: Formula) -> int:
        query = """
            INSERT INTO formulas (
                codigo_formula,
                nombre_formula,
                version_formula,
                activo,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    formula.codigo_formula,
                    formula.nombre_formula,
                    formula.version_formula,
                    int(formula.activo),
                    formula.observaciones,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def get_by_id(id_formula: int) -> Optional[Formula]:
        query = """
            SELECT *
            FROM formulas
            WHERE id_formula = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (id_formula,)).fetchone()

        return Formula.from_row(row) if row else None

    @staticmethod
    def get_by_codigo_version(
        codigo_formula: str,
        version_formula: str,
    ) -> Optional[Formula]:
        query = """
            SELECT *
            FROM formulas
            WHERE codigo_formula = ?
              AND version_formula = ?
        """

        with get_connection() as conn:
            row = conn.execute(query, (codigo_formula, version_formula)).fetchone()

        return Formula.from_row(row) if row else None

    @staticmethod
    def list_all(include_inactive: bool = True) -> list[Formula]:
        query = "SELECT * FROM formulas"
        params: tuple = ()

        if not include_inactive:
            query += " WHERE activo = 1"

        query += " ORDER BY nombre_formula, version_formula"

        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

        return [Formula.from_row(row) for row in rows]

    @staticmethod
    def update(formula: Formula) -> bool:
        if formula.id_formula is None:
            raise ValueError("No se puede actualizar una fórmula sin id_formula.")

        query = """
            UPDATE formulas
            SET
                codigo_formula = ?,
                nombre_formula = ?,
                version_formula = ?,
                activo = ?,
                observaciones = ?
            WHERE id_formula = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    formula.codigo_formula,
                    formula.nombre_formula,
                    formula.version_formula,
                    int(formula.activo),
                    formula.observaciones,
                    formula.id_formula,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(id_formula: int) -> bool:
        query = """
            DELETE FROM formulas
            WHERE id_formula = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_formula,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def deactivate(id_formula: int) -> bool:
        query = """
            UPDATE formulas
            SET activo = 0
            WHERE id_formula = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_formula,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def add_detalle(detalle: FormulaDetalle) -> int:
        query = """
            INSERT INTO formula_detalle (
                id_formula,
                id_insumo,
                cantidad,
                unidad,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    detalle.id_formula,
                    detalle.id_insumo,
                    detalle.cantidad,
                    detalle.unidad,
                    detalle.observaciones,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    @staticmethod
    def list_detalle_by_formula(id_formula: int) -> list[FormulaDetalle]:
        query = """
            SELECT *
            FROM formula_detalle
            WHERE id_formula = ?
            ORDER BY id_formula_detalle
        """

        with get_connection() as conn:
            rows = conn.execute(query, (id_formula,)).fetchall()

        return [FormulaDetalle.from_row(row) for row in rows]

    @staticmethod
    def delete_detalle(id_formula_detalle: int) -> bool:
        query = """
            DELETE FROM formula_detalle
            WHERE id_formula_detalle = ?
        """

        with get_connection() as conn:
            cursor = conn.execute(query, (id_formula_detalle,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def replace_detalle(
        id_formula: int,
        detalles: list[FormulaDetalle],
    ) -> None:
        delete_query = """
            DELETE FROM formula_detalle
            WHERE id_formula = ?
        """

        insert_query = """
            INSERT INTO formula_detalle (
                id_formula,
                id_insumo,
                cantidad,
                unidad,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?)
        """

        with get_connection() as conn:
            conn.execute(delete_query, (id_formula,))

            for detalle in detalles:
                conn.execute(
                    insert_query,
                    (
                        id_formula,
                        detalle.id_insumo,
                        detalle.cantidad,
                        detalle.unidad,
                        detalle.observaciones,
                    ),
                )

            conn.commit()
