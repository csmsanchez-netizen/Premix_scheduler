from __future__ import annotations

import math

from models.linea import Linea
from models.orden_produccion import OrdenProduccion
from repositories.lineas_repository import LineasRepository


class LineasService:
    """
    Servicio para evaluar factibilidad de órdenes en líneas.
    """

    @staticmethod
    def obtener_lineas_activas() -> list[Linea]:
        return LineasRepository.list_all(include_inactive=False)

    @staticmethod
    def calcular_batches(orden: OrdenProduccion, linea: Linea) -> int:
        if linea.tonelaje_batch <= 0:
            raise ValueError("El tonelaje batch de la línea debe ser mayor que cero.")

        return math.ceil(orden.toneladas / linea.tonelaje_batch)

    @staticmethod
    def calcular_tiempo_estimado_horas(
        orden: OrdenProduccion,
        linea: Linea,
    ) -> float | None:
        if linea.capacidad_tn_hora is None:
            return None
        if linea.capacidad_tn_hora <= 0:
            return None

        return orden.toneladas / linea.capacidad_tn_hora

    @staticmethod
    def es_linea_factible(orden: OrdenProduccion, linea: Linea) -> bool:
        if not linea.activo:
            return False

        if orden.id_linea_preferida is not None:
            return linea.id_linea == orden.id_linea_preferida

        return True

    @staticmethod
    def obtener_lineas_factibles(orden: OrdenProduccion) -> list[Linea]:
        lineas = LineasService.obtener_lineas_activas()
        return [linea for linea in lineas if LineasService.es_linea_factible(orden, linea)]

    @staticmethod
    def describir_factibilidad(orden: OrdenProduccion) -> list[dict]:
        resultado: list[dict] = []

        for linea in LineasService.obtener_lineas_factibles(orden):
            resultado.append(
                {
                    "id_linea": linea.id_linea,
                    "codigo_linea": linea.codigo_linea,
                    "nombre_linea": linea.nombre_linea,
                    "batches_estimados": LineasService.calcular_batches(orden, linea),
                    "tiempo_estimado_horas": LineasService.calcular_tiempo_estimado_horas(
                        orden, linea
                    ),
                }
            )

        return resultado
