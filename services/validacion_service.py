from __future__ import annotations

from dataclasses import dataclass, field

from repositories.formulas_repository import FormulasRepository
from repositories.lineas_repository import LineasRepository
from repositories.ordenes_repository import OrdenesRepository
from repositories.reglas_repository import ReglasRepository


@dataclass
class ResultadoValidacion:
    errores: list[str] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)

    def es_valido(self) -> bool:
        return len(self.errores) == 0


class ValidacionService:
    """
    Servicio para validar datos mínimos antes de secuenciar.
    """

    @staticmethod
    def validar_formulas() -> ResultadoValidacion:
        resultado = ResultadoValidacion()
        formulas = FormulasRepository.list_all(include_inactive=False)

        if not formulas:
            resultado.errores.append("No existen fórmulas activas.")
            return resultado

        for formula in formulas:
            detalles = FormulasRepository.list_detalle_by_formula(formula.id_formula)
            if not detalles:
                resultado.errores.append(
                    f"La fórmula {formula.codigo_formula} - {formula.nombre_formula} "
                    "no tiene insumos asociados."
                )

        return resultado

    @staticmethod
    def validar_lineas() -> ResultadoValidacion:
        resultado = ResultadoValidacion()
        lineas = LineasRepository.list_all(include_inactive=False)

        if not lineas:
            resultado.errores.append("No existen líneas activas.")
            return resultado

        for linea in lineas:
            if linea.tonelaje_batch <= 0:
                resultado.errores.append(
                    f"La línea {linea.codigo_linea} tiene tonelaje batch inválido."
                )

        return resultado

    @staticmethod
    def validar_ops() -> ResultadoValidacion:
        resultado = ResultadoValidacion()
        ordenes = OrdenesRepository.list_pendientes()

        if not ordenes:
            resultado.alertas.append("No hay órdenes pendientes para planificar.")
            return resultado

        for orden in ordenes:
            formula = FormulasRepository.get_by_id(orden.id_formula)
            if formula is None:
                resultado.errores.append(
                    f"La OP {orden.numero_op} referencia una fórmula inexistente."
                )
            elif not formula.activo:
                resultado.alertas.append(
                    f"La OP {orden.numero_op} usa una fórmula inactiva."
                )

            if orden.toneladas <= 0:
                resultado.errores.append(
                    f"La OP {orden.numero_op} tiene toneladas inválidas."
                )

        return resultado

    @staticmethod
    def validar_matriz_riesgo() -> ResultadoValidacion:
        resultado = ResultadoValidacion()
        reglas = ReglasRepository.list_all(include_inactive=False)

        if not reglas:
            resultado.errores.append("La matriz de riesgo no tiene reglas activas.")

        return resultado

    @staticmethod
    def validar_datos_planificacion() -> ResultadoValidacion:
        resultado = ResultadoValidacion()

        for parcial in (
            ValidacionService.validar_formulas(),
            ValidacionService.validar_lineas(),
            ValidacionService.validar_ops(),
            ValidacionService.validar_matriz_riesgo(),
        ):
            resultado.errores.extend(parcial.errores)
            resultado.alertas.extend(parcial.alertas)

        return resultado
