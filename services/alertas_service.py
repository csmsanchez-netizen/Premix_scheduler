from __future__ import annotations

from typing import Any

from services.validacion_service import ValidacionService


class AlertasService:
    """
    Servicio para consolidar alertas técnicas y operativas
    en mensajes simples para el usuario.
    """

    @staticmethod
    def generar_alertas_validacion() -> dict[str, list[str]]:
        resultado = ValidacionService.validar_datos_planificacion()
        return {
            "errores": resultado.errores,
            "alertas": resultado.alertas,
        }

    @staticmethod
    def generar_alertas_secuencia(resultado_secuencia: dict[str, Any]) -> list[str]:
        alertas: list[str] = []

        for op in resultado_secuencia.get("ops_no_asignadas", []):
            alertas.append(
                f"OP {op['numero_op']} no asignada: {op['motivo']}"
            )

        if not resultado_secuencia.get("registros"):
            alertas.append("No se generaron registros de secuencia.")

        return alertas

    @staticmethod
    def consolidar_alertas(resultado_secuencia: dict[str, Any] | None = None) -> dict[str, list[str]]:
        base = AlertasService.generar_alertas_validacion()

        if resultado_secuencia is None:
            return base

        alertas_secuencia = AlertasService.generar_alertas_secuencia(resultado_secuencia)

        return {
            "errores": base["errores"],
            "alertas": base["alertas"] + alertas_secuencia,
        }
