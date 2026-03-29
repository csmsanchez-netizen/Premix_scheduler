from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional

from config.settings import ESTADOS_OP


@dataclass
class OrdenProduccion:
    """
    Modelo de dominio para una orden de producción.
    """

    id_op: Optional[int]
    numero_op: str
    fecha_op: str
    id_formula: int
    toneladas: float
    prioridad: int = 0
    fecha_compromiso: Optional[str] = None
    id_linea_preferida: Optional[int] = None
    estado: str = "PENDIENTE"
    observaciones: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.numero_op:
            raise ValueError("El número de OP no puede estar vacío.")
        if not self.fecha_op:
            raise ValueError("La fecha de la OP es obligatoria.")
        if self.id_formula <= 0:
            raise ValueError("id_formula debe ser mayor que cero.")
        if self.toneladas <= 0:
            raise ValueError("Las toneladas deben ser mayores que cero.")
        if self.prioridad < 0:
            raise ValueError("La prioridad no puede ser negativa.")
        if self.id_linea_preferida is not None and self.id_linea_preferida <= 0:
            raise ValueError("id_linea_preferida debe ser mayor que cero.")
        if self.estado not in ESTADOS_OP:
            raise ValueError(
                f"Estado inválido: {self.estado}. Debe ser uno de {ESTADOS_OP}."
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "OrdenProduccion":
        return OrdenProduccion(
            id_op=row["id_op"],
            numero_op=row["numero_op"],
            fecha_op=row["fecha_op"],
            id_formula=row["id_formula"],
            toneladas=float(row["toneladas"]),
            prioridad=row["prioridad"],
            fecha_compromiso=row["fecha_compromiso"],
            id_linea_preferida=row["id_linea_preferida"],
            estado=row["estado"],
            observaciones=row["observaciones"],
        )
