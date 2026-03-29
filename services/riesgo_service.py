from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from config.settings import (
    DEFAULT_DATETIME_FORMAT,
    JERARQUIA_CATEGORIAS,
    JERARQUIA_LIMPIEZA,
    JERARQUIA_RIESGO,
)
from models.insumo import Insumo
from repositories.formulas_repository import FormulasRepository
from repositories.insumos_repository import InsumosRepository


@dataclass
class PerfilRiesgoFormula:
    """
    Resultado calculado del perfil de riesgo de una fórmula.
    """

    id_formula: int
    categoria_dominante: str
    nivel_riesgo_resultante: str
    limpieza_sugerida: str | None
    contiene_critico: bool
    detalle_riesgo: str
    fecha_calculo: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_formula": self.id_formula,
            "categoria_dominante": self.categoria_dominante,
            "nivel_riesgo_resultante": self.nivel_riesgo_resultante,
            "limpieza_sugerida": self.limpieza_sugerida,
            "contiene_critico": int(self.contiene_critico),
            "detalle_riesgo": self.detalle_riesgo,
            "fecha_calculo": self.fecha_calculo,
        }


class RiesgoService:
    """
    Servicio para calcular el perfil de riesgo de una fórmula
    a partir de los insumos que la componen.
    """

    @staticmethod
    def obtener_insumos_de_formula(id_formula: int) -> list[Insumo]:
        detalles = FormulasRepository.list_detalle_by_formula(id_formula)
        insumos: list[Insumo] = []

        for detalle in detalles:
            insumo = InsumosRepository.get_by_id(detalle.id_insumo)
            if insumo is not None:
                insumos.append(insumo)

        return insumos

    @staticmethod
    def calcular_nivel_riesgo(insumos: list[Insumo]) -> str:
        if not insumos:
            raise ValueError("La fórmula no tiene insumos para calcular riesgo.")

        max_riesgo = 0
        nivel_resultante = "BAJO"

        for insumo in insumos:
            nivel = (insumo.nivel_riesgo or "").strip().upper()
            puntaje = JERARQUIA_RIESGO.get(nivel, 0)

            if puntaje > max_riesgo:
                max_riesgo = puntaje
                nivel_resultante = nivel

        if any(insumo.es_critico for insumo in insumos):
            return "CRITICO"

        return nivel_resultante

    @staticmethod
    def calcular_categoria_dominante(insumos: list[Insumo]) -> str:
        if not insumos:
            raise ValueError("La fórmula no tiene insumos para calcular categoría.")

        max_categoria = 0
        categoria_resultante = "BASE"

        for insumo in insumos:
            categoria = (insumo.categoria_riesgo or "").strip().upper()
            puntaje = JERARQUIA_CATEGORIAS.get(categoria, 0)

            if puntaje > max_categoria:
                max_categoria = puntaje
                categoria_resultante = categoria

        return categoria_resultante

    @staticmethod
    def calcular_limpieza_sugerida(insumos: list[Insumo]) -> str | None:
        if not insumos:
            return None

        max_limpieza = -1
        limpieza_resultante: str | None = None

        for insumo in insumos:
            limpieza = (insumo.limpieza_sugerida or "").strip().upper()
            if not limpieza:
                continue

            puntaje = JERARQUIA_LIMPIEZA.get(limpieza, -1)
            if puntaje > max_limpieza:
                max_limpieza = puntaje
                limpieza_resultante = limpieza

        return limpieza_resultante

    @staticmethod
    def construir_detalle_riesgo(insumos: list[Insumo]) -> str:
        if not insumos:
            return "Sin insumos asociados."

        partes: list[str] = []

        criticos = [i.codigo_insumo for i in insumos if i.es_critico]
        if criticos:
            partes.append(
                f"Insumos críticos detectados: {', '.join(sorted(criticos))}."
            )

        categorias = sorted({(i.categoria_riesgo or "").strip().upper() for i in insumos})
        if categorias:
            partes.append(f"Categorías presentes: {', '.join(categorias)}.")

        limpiezas = sorted(
            {
                (i.limpieza_sugerida or "").strip().upper()
                for i in insumos
                if i.limpieza_sugerida
            }
        )
        if limpiezas:
            partes.append(f"Limpiezas sugeridas detectadas: {', '.join(limpiezas)}.")

        return " ".join(partes) if partes else "Perfil calculado sin observaciones adicionales."

    @staticmethod
    def calcular_perfil_formula(id_formula: int) -> PerfilRiesgoFormula:
        insumos = RiesgoService.obtener_insumos_de_formula(id_formula)

        if not insumos:
            raise ValueError(
                f"La fórmula con id {id_formula} no tiene insumos asociados."
            )

        categoria_dominante = RiesgoService.calcular_categoria_dominante(insumos)
        nivel_riesgo_resultante = RiesgoService.calcular_nivel_riesgo(insumos)
        limpieza_sugerida = RiesgoService.calcular_limpieza_sugerida(insumos)
        contiene_critico = any(insumo.es_critico for insumo in insumos)
        detalle_riesgo = RiesgoService.construir_detalle_riesgo(insumos)
        fecha_calculo = datetime.now().strftime(DEFAULT_DATETIME_FORMAT)

        return PerfilRiesgoFormula(
            id_formula=id_formula,
            categoria_dominante=categoria_dominante,
            nivel_riesgo_resultante=nivel_riesgo_resultante,
            limpieza_sugerida=limpieza_sugerida,
            contiene_critico=contiene_critico,
            detalle_riesgo=detalle_riesgo,
            fecha_calculo=fecha_calculo,
        )
