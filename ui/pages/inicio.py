from __future__ import annotations

import streamlit as st

from repositories.formulas_repository import FormulasRepository
from repositories.insumos_repository import InsumosRepository
from repositories.lineas_repository import LineasRepository
from repositories.ordenes_repository import OrdenesRepository
from repositories.reglas_repository import ReglasRepository
from services.alertas_service import AlertasService


def render_inicio() -> None:
    st.title("🏭 Premix Scheduler")
    st.subheader("Resumen general del sistema")

    insumos = InsumosRepository.list_all()
    formulas = FormulasRepository.list_all()
    lineas = LineasRepository.list_all()
    ordenes = OrdenesRepository.list_all()
    reglas = ReglasRepository.list_all()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Insumos", len(insumos))
    c2.metric("Fórmulas", len(formulas))
    c3.metric("Líneas", len(lineas))
    c4.metric("OPs", len(ordenes))
    c5.metric("Reglas", len(reglas))

    st.markdown("---")
    st.subheader("Estado de validación")

    alertas = AlertasService.generar_alertas_validacion()

    if not alertas["errores"] and not alertas["alertas"]:
        st.success("No se detectaron errores ni alertas.")
        return

    if alertas["errores"]:
        st.error("Errores detectados")
        for error in alertas["errores"]:
            st.write(f"- {error}")

    if alertas["alertas"]:
        st.warning("Alertas detectadas")
        for alerta in alertas["alertas"]:
            st.write(f"- {alerta}")

    st.markdown("---")
    st.info(
        "Siguiente paso sugerido: ir a la página Secuenciador para validar y ejecutar "
        "una corrida básica."
    )
