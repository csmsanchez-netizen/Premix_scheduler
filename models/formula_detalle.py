from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class FormulaDetalle:
    """
    Modelo de dominio para el detalle de una fórmula.
    Relaciona una fórmula con un insumo y su cantidad.
    """

    id_formula_detalle: Optional[int]
    id_formula: int
    id_insumo: int
    cantidad: float
    unidad: str
    observaciones: Optional[str] = None

    def __post_init__(self) -> None:
        if self.id_formula <= 0:
            raise ValueError("id_formula debe ser mayor que cero.")
        if self.id_insumo <= 0:
            raise ValueError("id_insumo debe ser mayor que cero.")
        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if not self.unidad:
            raise ValueError("La unidad es obligatoria.")

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el modelo a diccionario.
        """
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "FormulaDetalle":
        """
        Crea una instancia de FormulaDetalle a partir de una fila sqlite3.Row.
        """
        return FormulaDetalle(
            id_formula_detalle=row["id_formula_detalle"],
            id_formula=row["id_formula"],
            id_insumo=row["id_insumo"],
            cantidad=float(row["cantidad"]),
            unidad=row["unidad"],
            observaciones=row["observaciones"],
        )
