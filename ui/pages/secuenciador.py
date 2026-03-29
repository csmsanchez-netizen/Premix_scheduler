from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from services.alertas_service import AlertasService
from services.exportacion_service import ExportacionService
from services.secuenciador_service import SecuenciadorService
from services.validacion_service import ValidacionService


def _mostrar_registros(resultado_secuencia: dict) -> None:
    registros = resultado_secuencia.get("registros", [])
    ops_no_asignadas = resultado_secuencia.get("ops_no_asignadas", [])

    st.subheader("Resultado de secuencia")

    if not registros:
        st.warning("No se generaron registros de secuencia.")
    else:
        st.dataframe(registros, use_container_width=True)

    if ops_no_asignadas:
        st.subheader("OPs no asignadas")
        st.dataframe(ops_no_asignadas, use_container_width=True)


def _mostrar_alertas(alertas: dict[str, list[str]]) -> None:
    if alertas["errores"]:
        st.error("Errores")
        for item in alertas["errores"]:
            st.write(f"- {item}")

    if alertas["alertas"]:
        st.warning("Alertas")
        for item in alertas["alertas"]:
            st.write(f"- {item}")

    if not alertas["errores"] and not alertas["alertas"]:
        st.success("Sin errores ni alertas.")


def render_secuenciador() -> None:
    st.title("⚙️ Secuenciador MVP")
    st.write("Ejecuta una corrida básica del secuenciador.")

    st.subheader("1. Validación previa")
    resultado_validacion = ValidacionService.validar_datos_planificacion()

    _mostrar_alertas(
        {
            "errores": resultado_validacion.errores,
            "alertas": resultado_validacion.alertas,
        }
    )

    puede_ejecutar = resultado_validacion.es_valido()

    st.markdown("---")
    st.subheader("2. Ejecutar secuencia")

    if not puede_ejecutar:
        st.info("Corrige los errores bloqueantes antes de ejecutar.")
        return

    if st.button("Generar secuencia", type="primary"):
        resultado_secuencia = SecuenciadorService.generar_secuencia()
        alertas = AlertasService.consolidar_alertas(resultado_secuencia)

        st.session_state["resultado_secuencia"] = resultado_secuencia
        st.session_state["alertas_secuencia"] = alertas

    if "resultado_secuencia" in st.session_state:
        resultado_secuencia = st.session_state["resultado_secuencia"]
        alertas = st.session_state["alertas_secuencia"]

        st.markdown("---")
        st.subheader("3. Alertas finales")
        _mostrar_alertas(alertas)

        st.markdown("---")
        _mostrar_registros(resultado_secuencia)

        st.markdown("---")
        st.subheader("4. Exportación")

        if st.button("Exportar a Excel"):
            output_path = ExportacionService.exportar_resultado(
                resultado_secuencia=resultado_secuencia,
                alertas=alertas,
            )
            st.success(f"Archivo exportado: {output_path}")

        st.subheader("5. Vista JSON")
        st.code(
            json.dumps(resultado_secuencia, indent=2, ensure_ascii=False),
            language="json",
        )

        default_path = Path("exports/secuencia_produccion.xlsx")
        st.caption(f"Ruta de exportación por defecto: {default_path}")
