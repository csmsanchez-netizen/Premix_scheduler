from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class Linea:
    """
    Modelo de dominio para una línea o mezcladora.
    """

    id_linea: Optional[int]
    codigo_linea: str
    nombre_linea: str
    tonelaje_batch: float
    capacidad_tn_hora: Optional[float] = None
    activo: bool = True
    tiempo_limpieza_corta_min: Optional[int] = None
    tiempo_limpieza_profunda_min: Optional[int] = None
    tiempo_flush_min: Optional[int] = None
    observaciones: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.codigo_linea:
            raise ValueError("El código de línea no puede estar vacío.")
        if not self.nombre_linea:
            raise ValueError("El nombre de línea no puede estar vacío.")
        if self.tonelaje_batch <= 0:
            raise ValueError("El tonelaje por batch debe ser mayor que cero.")

        if self.capacidad_tn_hora is not None and self.capacidad_tn_hora <= 0:
            raise ValueError("La capacidad tn/hora debe ser mayor que cero.")

        for field_name, value in (
            ("tiempo_limpieza_corta_min", self.tiempo_limpieza_corta_min),
            ("tiempo_limpieza_profunda_min", self.tiempo_limpieza_profunda_min),
            ("tiempo_flush_min", self.tiempo_flush_min),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{field_name} no puede ser negativo.")

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el modelo a diccionario.
        """
        return asdict(self)

    @staticmethod
    def from_row(row: Any) -> "Linea":
        """
        Crea una instancia de Linea a partir de una fila sqlite3.Row.
        """
        return Linea(
            id_linea=row["id_linea"],
            codigo_linea=row["codigo_linea"],
            nombre_linea=row["nombre_linea"],
            tonelaje_batch=float(row["tonelaje_batch"]),
            capacidad_tn_hora=(
                float(row["capacidad_tn_hora"])
                if row["capacidad_tn_hora"] is not None
                else None
            ),
            activo=bool(row["activo"]),
            tiempo_limpieza_corta_min=row["tiempo_limpieza_corta_min"],
            tiempo_limpieza_profunda_min=row["tiempo_limpieza_profunda_min"],
            tiempo_flush_min=row["tiempo_flush_min"],
            observaciones=row["observaciones"],
        )

    def is_active(self) -> bool:
        return self.activo
