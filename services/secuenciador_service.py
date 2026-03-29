from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from config.settings import (
    COSTO_FLUSH,
    COSTO_LIMPIEZA_CORTA,
    COSTO_LIMPIEZA_PROFUNDA,
    COSTO_TRANSICION_PERMITIDA,
    COSTO_TRANSICION_PROHIBIDA,
    DEFAULT_DATETIME_FORMAT,
)
from repositories.lineas_repository import LineasRepository
from repositories.ordenes_repository import OrdenesRepository
from repositories.reglas_repository import ReglasRepository
from services.lineas_service import LineasService
from services.riesgo_service import RiesgoService, PerfilRiesgoFormula


@dataclass
class EvaluacionTransicion:
    categoria_origen: str
    categoria_destino: str
    accion: str
    id_limpieza: int | None
    costo: int
    justificacion: str


class SecuenciadorService:
    """
    Servicio simple de secuenciación para MVP.
    Heurística:
    - toma OPs pendientes
    - busca líneas factibles
    - evalúa transición contra el último estado de cada línea
    - asigna la opción de menor costo
    """

    @staticmethod
    def _obtener_regla(categoria_origen: str, categoria_destino: str):
        reglas = ReglasRepository.get_rule(
            categoria_origen=categoria_origen,
            categoria_destino=categoria_destino,
            include_inactive=False,
        )
        return reglas[0] if reglas else None

    @staticmethod
    def _costo_por_accion(accion: str) -> int:
        accion = (accion or "").strip().upper()

        if accion == "PERMITIDO":
            return COSTO_TRANSICION_PERMITIDA
        if accion == "PERMITIDO_CON_FLUSH":
            return COSTO_FLUSH
        if accion == "PERMITIDO_CON_LIMPIEZA":
            return COSTO_LIMPIEZA_PROFUNDA
        if accion == "PROHIBIDO":
            return COSTO_TRANSICION_PROHIBIDA

        return COSTO_TRANSICION_PROHIBIDA

    @staticmethod
    def evaluar_transicion(
        perfil_origen: PerfilRiesgoFormula | None,
        perfil_destino: PerfilRiesgoFormula,
    ) -> EvaluacionTransicion:
        if perfil_origen is None:
            return EvaluacionTransicion(
                categoria_origen="INICIO",
                categoria_destino=perfil_destino.categoria_dominante,
                accion="PERMITIDO",
                id_limpieza=None,
                costo=COSTO_TRANSICION_PERMITIDA,
                justificacion="Inicio de línea o sin producto previo.",
            )

        regla = SecuenciadorService._obtener_regla(
            perfil_origen.categoria_dominante,
            perfil_destino.categoria_dominante,
        )

        if regla is None:
            return EvaluacionTransicion(
                categoria_origen=perfil_origen.categoria_dominante,
                categoria_destino=perfil_destino.categoria_dominante,
                accion="PROHIBIDO",
                id_limpieza=None,
                costo=COSTO_TRANSICION_PROHIBIDA,
                justificacion=(
                    "No existe regla activa en la matriz de riesgo para la transición "
                    f"{perfil_origen.categoria_dominante} -> "
                    f"{perfil_destino.categoria_dominante}."
                ),
            )

        return EvaluacionTransicion(
            categoria_origen=perfil_origen.categoria_dominante,
            categoria_destino=perfil_destino.categoria_dominante,
            accion=regla.accion,
            id_limpieza=regla.id_limpieza,
            costo=SecuenciadorService._costo_por_accion(regla.accion),
            justificacion=(
                f"Regla aplicada: {regla.categoria_origen} -> "
                f"{regla.categoria_destino} = {regla.accion}."
            ),
        )

    @staticmethod
    def _crear_estado_lineas() -> dict[int, dict[str, Any]]:
        estado: dict[int, dict[str, Any]] = {}

        for linea in LineasRepository.list_all(include_inactive=False):
            estado[linea.id_linea] = {
                "linea": linea,
                "ultimo_perfil": None,
                "posicion": 0,
                "registros": [],
            }

        return estado

    @staticmethod
    def _agregar_registro(
        estado_linea: dict[str, Any],
        tipo_registro: str,
        id_op: int | None,
        evaluacion: EvaluacionTransicion,
    ) -> None:
        estado_linea["posicion"] += 1
        estado_linea["registros"].append(
            {
                "id_linea": estado_linea["linea"].id_linea,
                "codigo_linea": estado_linea["linea"].codigo_linea,
                "nombre_linea": estado_linea["linea"].nombre_linea,
                "posicion": estado_linea["posicion"],
                "tipo_registro": tipo_registro,
                "id_op": id_op,
                "id_limpieza": evaluacion.id_limpieza if tipo_registro != "PRODUCCION" else None,
                "categoria_origen": evaluacion.categoria_origen,
                "categoria_destino": evaluacion.categoria_destino,
                "accion_transicion": evaluacion.accion,
                "justificacion": evaluacion.justificacion,
                "editado_manual": 0,
            }
        )

    @staticmethod
    def _crear_evento_limpieza_si_corresponde(
        estado_linea: dict[str, Any],
        evaluacion: EvaluacionTransicion,
    ) -> None:
        accion = (evaluacion.accion or "").strip().upper()

        if accion == "PERMITIDO_CON_LIMPIEZA":
            SecuenciadorService._agregar_registro(
                estado_linea=estado_linea,
                tipo_registro="LIMPIEZA",
                id_op=None,
                evaluacion=evaluacion,
            )
        elif accion == "PERMITIDO_CON_FLUSH":
            SecuenciadorService._agregar_registro(
                estado_linea=estado_linea,
                tipo_registro="FLUSH",
                id_op=None,
                evaluacion=evaluacion,
            )

    @staticmethod
    def _seleccionar_mejor_linea(
        orden,
        perfil_destino: PerfilRiesgoFormula,
        estado_lineas: dict[int, dict[str, Any]],
    ) -> tuple[Optional[dict[str, Any]], Optional[EvaluacionTransicion]]:
        mejores: list[tuple[int, dict[str, Any], EvaluacionTransicion]] = []

        for linea in LineasService.obtener_lineas_factibles(orden):
            estado_linea = estado_lineas.get(linea.id_linea)
            if estado_linea is None:
                continue

            perfil_origen = estado_linea["ultimo_perfil"]
            evaluacion = SecuenciadorService.evaluar_transicion(
                perfil_origen=perfil_origen,
                perfil_destino=perfil_destino,
            )

            if evaluacion.accion == "PROHIBIDO":
                continue

            mejores.append((evaluacion.costo, estado_linea, evaluacion))

        if not mejores:
            return None, None

        mejores.sort(key=lambda x: (x[0], x[1]["posicion"], x[1]["linea"].codigo_linea))
        _, estado_linea, evaluacion = mejores[0]
        return estado_linea, evaluacion

    @staticmethod
    def generar_secuencia() -> dict[str, Any]:
        ordenes = OrdenesRepository.list_pendientes()
        estado_lineas = SecuenciadorService._crear_estado_lineas()

        resultado = {
            "fecha_generacion": datetime.now().strftime(DEFAULT_DATETIME_FORMAT),
            "criterio_planificacion": "Heurística greedy por menor costo de transición",
            "registros": [],
            "ops_no_asignadas": [],
        }

        for orden in ordenes:
            perfil = RiesgoService.calcular_perfil_formula(orden.id_formula)

            estado_linea, evaluacion = SecuenciadorService._seleccionar_mejor_linea(
                orden=orden,
                perfil_destino=perfil,
                estado_lineas=estado_lineas,
            )

            if estado_linea is None or evaluacion is None:
                resultado["ops_no_asignadas"].append(
                    {
                        "id_op": orden.id_op,
                        "numero_op": orden.numero_op,
                        "motivo": "No se encontró línea factible con transición permitida.",
                    }
                )
                continue

            SecuenciadorService._crear_evento_limpieza_si_corresponde(
                estado_linea=estado_linea,
                evaluacion=evaluacion,
            )

            SecuenciadorService._agregar_registro(
                estado_linea=estado_linea,
                tipo_registro="PRODUCCION",
                id_op=orden.id_op,
                evaluacion=evaluacion,
            )

            estado_linea["ultimo_perfil"] = perfil

        for estado_linea in estado_lineas.values():
            resultado["registros"].extend(estado_linea["registros"])

        resultado["registros"].sort(key=lambda x: (x["codigo_linea"], x["posicion"]))
        return resultado
