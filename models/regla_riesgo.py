from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional

from config.settings import ACCIONES_TRANSICION


@dataclass
class ReglaRiesgo:
    """
    Modelo de dominio para una regla de transición de riesgo.
    """

    id_regla: Optional[int]
    categoria_origen: str
    categoria_destino: str
    accion: str
    id_limpieza: Optional[int] = None
    prioridad: int = 1
    activo: bool = True
    observaciones: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.categoria_origen:
            raise ValueError("La categoría de origen es obligatoria.")
        if not self.categoria_destino:
            raise ValueError("La categoría de destino es obligatoria.")
        if not self.accion:
            raise ValueError("La acción es obligatoria.")
        if self.accion not in ACCIONES_TRANSICION:
            raise ValueError(
                f"Acción inválida: {self.accion}. Debe ser una de {ACCIONES_TRANSICION}."
            )
        if self.prioridad <= 0:
            raise ValueError("La prioridad debe ser mayor que cero.")
        if self.id_limpieza is not None and self.id_limpieza <= 0:
            raise ValueError("id_limpieza debe ser mayor que cero cuando se informa.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "ReglaRiesgo":
        return ReglaRiesgo(
            id_regla=row["id_regla"],
            categoria_origen=row["categoria_origen"],
            categoria_destino=row["categoria_destino"],
            accion=row["accion"],
            id_limpieza=row["id_limpieza"],
            prioridad=row["prioridad"],
            activo=bool(row["activo"]),
            observaciones=row["observaciones"],
        )

    def is_active(self) -> bool:
        return self.activo
