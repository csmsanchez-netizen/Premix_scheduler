from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class Formula:
    """
    Modelo de dominio para una fórmula.
    """

    id_formula: Optional[int]
    codigo_formula: str
    nombre_formula: str
    version_formula: str
    activo: bool = True
    observaciones: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.codigo_formula:
            raise ValueError("El código de fórmula no puede estar vacío.")
        if not self.nombre_formula:
            raise ValueError("El nombre de fórmula no puede estar vacío.")
        if not self.version_formula:
            raise ValueError("La versión de la fórmula es obligatoria.")

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el modelo a diccionario.
        """
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "Formula":
        """
        Crea una instancia de Formula a partir de una fila sqlite3.Row.
        """
        return Formula(
            id_formula=row["id_formula"],
            codigo_formula=row["codigo_formula"],
            nombre_formula=row["nombre_formula"],
            version_formula=row["version_formula"],
            activo=bool(row["activo"]),
            observaciones=row["observaciones"],
        )

    def is_active(self) -> bool:
        return self.activo
