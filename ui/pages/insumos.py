from __future__ import annotations

import streamlit as st

from models.insumo import Insumo
from repositories.insumos_repository import InsumosRepository


CATEGORIAS_RIESGO = [
    "BASE",
    "MINERAL",
    "ALTA_RESTRICCION",
    "COCCIDIOSTATO",
    "MEDICADO",
]

NIVELES_RIESGO = [
    "BAJO",
    "MEDIO",
    "ALTO",
    "CRITICO",
]

LIMPIEZAS = [
    "",
    "NINGUNA",
    "CORTA",
    "FLUSH",
    "PROFUNDA",
]


def _reset_form() -> None:
    st.session_state["insumo_edit_id"] = None
    st.session_state["insumo_codigo"] = ""
    st.session_state["insumo_nombre"] = ""
    st.session_state["insumo_categoria"] = CATEGORIAS_RIESGO[0]
    st.session_state["insumo_nivel"] = NIVELES_RIESGO[0]
    st.session_state["insumo_activo"] = True
    st.session_state["insumo_limpieza"] = ""
    st.session_state["insumo_critico"] = False
    st.session_state["insumo_observaciones"] = ""


def _load_insumo_to_form(insumo: Insumo) -> None:
    st.session_state["insumo_edit_id"] = insumo.id_insumo
    st.session_state["insumo_codigo"] = insumo.codigo_insumo
    st.session_state["insumo_nombre"] = insumo.nombre_insumo
    st.session_state["insumo_categoria"] = insumo.categoria_riesgo
    st.session_state["insumo_nivel"] = insumo.nivel_riesgo
    st.session_state["insumo_activo"] = insumo.activo
    st.session_state["insumo_limpieza"] = insumo.limpieza_sugerida or ""
    st.session_state["insumo_critico"] = insumo.es_critico
    st.session_state["insumo_observaciones"] = insumo.observaciones or ""


def _save_insumo() -> None:
    try:
        insumo = Insumo(
            id_insumo=st.session_state.get("insumo_edit_id"),
            codigo_insumo=st.session_state["insumo_codigo"].strip().upper(),
            nombre_insumo=st.session_state["insumo_nombre"].strip(),
            categoria_riesgo=st.session_state["insumo_categoria"].strip().upper(),
            nivel_riesgo=st.session_state["insumo_nivel"].strip().upper(),
            activo=bool(st.session_state["insumo_activo"]),
            limpieza_sugerida=(
                st.session_state["insumo_limpieza"].strip().upper() or None
            ),
            es_critico=bool(st.session_state["insumo_critico"]),
            observaciones=st.session_state["insumo_observaciones"].strip() or None,
        )

        if insumo.id_insumo is None:
            existente = InsumosRepository.get_by_codigo(insumo.codigo_insumo)
            if existente is not None:
                st.error("Ya existe un insumo con ese código.")
                return
            InsumosRepository.create(insumo)
            st.success("Insumo creado correctamente.")
        else:
            existente = InsumosRepository.get_by_codigo(insumo.codigo_insumo)
            if existente is not None and existente.id_insumo != insumo.id_insumo:
                st.error("Ya existe otro insumo con ese código.")
                return
            actualizado = InsumosRepository.update(insumo)
            if actualizado:
                st.success("Insumo actualizado correctamente.")
            else:
                st.warning("No se realizaron cambios.")

        _reset_form()

    except Exception as exc:
        st.error(f"Error al guardar el insumo: {exc}")


def render_insumos() -> None:
    st.title("📦 Insumos")
    st.write("Crear, listar y editar insumos del sistema.")

    if "insumo_edit_id" not in st.session_state:
        _reset_form()

    with st.form("form_insumo", clear_on_submit=False):
        st.subheader("Formulario de insumo")

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Código", key="insumo_codigo")
            st.selectbox("Categoría de riesgo", CATEGORIAS_RIESGO, key="insumo_categoria")
            st.checkbox("Activo", key="insumo_activo")
            st.checkbox("Es crítico", key="insumo_critico")

        with col2:
            st.text_input("Nombre", key="insumo_nombre")
            st.selectbox("Nivel de riesgo", NIVELES_RIESGO, key="insumo_nivel")
            st.selectbox("Limpieza sugerida", LIMPIEZAS, key="insumo_limpieza")

        st.text_area("Observaciones", key="insumo_observaciones")

        c1, c2 = st.columns(2)
        guardar = c1.form_submit_button("Guardar")
        limpiar = c2.form_submit_button("Limpiar formulario")

        if guardar:
            _save_insumo()

        if limpiar:
            _reset_form()
            st.rerun()

    st.markdown("---")
    st.subheader("Listado de insumos")

    insumos = InsumosRepository.list_all(include_inactive=True)

    if not insumos:
        st.info("No hay insumos registrados.")
        return

    for insumo in insumos:
        with st.expander(f"{insumo.codigo_insumo} - {insumo.nombre_insumo}"):
            st.write(f"**Categoría:** {insumo.categoria_riesgo}")
            st.write(f"**Nivel de riesgo:** {insumo.nivel_riesgo}")
            st.write(f"**Limpieza sugerida:** {insumo.limpieza_sugerida or '-'}")
            st.write(f"**Crítico:** {'Sí' if insumo.es_critico else 'No'}")
            st.write(f"**Activo:** {'Sí' if insumo.activo else 'No'}")
            st.write(f"**Observaciones:** {insumo.observaciones or '-'}")

            c1, c2 = st.columns(2)
            if c1.button("Editar", key=f"edit_insumo_{insumo.id_insumo}"):
                _load_insumo_to_form(insumo)
                st.rerun()

            if c2.button("Desactivar", key=f"deact_insumo_{insumo.id_insumo}"):
                if insumo.activo:
                    InsumosRepository.deactivate(insumo.id_insumo)
                    st.success("Insumo desactivado.")
                    st.rerun()
                else:
                    st.info("El insumo ya está desactivado.")
