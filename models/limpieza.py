from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class Limpieza:
    """
    Modelo de dominio para un tipo de limpieza.
    """

    id_limpieza: Optional[int]
    codigo_limpieza: str
    nombre_limpieza: str
    duracion_min: Optional[int] = None
    activo: bool = True
    descripcion: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.codigo_limpieza:
            raise ValueError("El código de limpieza no puede estar vacío.")
        if not self.nombre_limpieza:
            raise ValueError("El nombre de limpieza no puede estar vacío.")
        if self.duracion_min is not None and self.duracion_min < 0:
            raise ValueError("La duración de limpieza no puede ser negativa.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "Limpieza":
        return Limpieza(
            id_limpieza=row["id_limpieza"],
            codigo_limpieza=row["codigo_limpieza"],
            nombre_limpieza=row["nombre_limpieza"],
            duracion_min=row["duracion_min"],
            activo=bool(row["activo"]),
            descripcion=row["descripcion"],
        )

    def is_active(self) -> bool:
        return self.activo
