from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class Insumo:
    """
    Modelo de dominio para un insumo.
    """

    id_insumo: Optional[int]
    codigo_insumo: str
    nombre_insumo: str
    categoria_riesgo: str
    nivel_riesgo: str
    activo: bool = True
    limpieza_sugerida: Optional[str] = None
    es_critico: bool = False
    observaciones: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.codigo_insumo:
            raise ValueError("El código de insumo no puede estar vacío.")
        if not self.nombre_insumo:
            raise ValueError("El nombre de insumo no puede estar vacío.")
        if not self.categoria_riesgo:
            raise ValueError("La categoría de riesgo es obligatoria.")
        if not self.nivel_riesgo:
            raise ValueError("El nivel de riesgo es obligatorio.")

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el modelo a diccionario.
        """
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "Insumo":
        """
        Crea una instancia de Insumo a partir de una fila sqlite3.Row.
        """
        return Insumo(
            id_insumo=row["id_insumo"],
            codigo_insumo=row["codigo_insumo"],
            nombre_insumo=row["nombre_insumo"],
            categoria_riesgo=row["categoria_riesgo"],
            nivel_riesgo=row["nivel_riesgo"],
            activo=bool(row["activo"]),
            limpieza_sugerida=row["limpieza_sugerida"],
            es_critico=bool(row["es_critico"]),
            observaciones=row["observaciones"],
        )

    def is_active(self) -> bool:
        return self.activo

    def is_critical(self) -> bool:
        return self.es_critico
