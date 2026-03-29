from __future__ import annotations

import streamlit as st

from models.linea import Linea
from repositories.lineas_repository import LineasRepository


def _reset_linea_form() -> None:
    st.session_state["linea_edit_id"] = None
    st.session_state["linea_codigo"] = ""
    st.session_state["linea_nombre"] = ""
    st.session_state["linea_tonelaje_batch"] = 1.0
    st.session_state["linea_capacidad"] = 0.0
    st.session_state["linea_activa"] = True
    st.session_state["linea_limpieza_corta"] = 0
    st.session_state["linea_limpieza_profunda"] = 0
    st.session_state["linea_flush"] = 0
    st.session_state["linea_observaciones"] = ""


def _load_linea_to_form(linea: Linea) -> None:
    st.session_state["linea_edit_id"] = linea.id_linea
    st.session_state["linea_codigo"] = linea.codigo_linea
    st.session_state["linea_nombre"] = linea.nombre_linea
    st.session_state["linea_tonelaje_batch"] = float(linea.tonelaje_batch)
    st.session_state["linea_capacidad"] = float(linea.capacidad_tn_hora or 0.0)
    st.session_state["linea_activa"] = linea.activo
    st.session_state["linea_limpieza_corta"] = int(linea.tiempo_limpieza_corta_min or 0)
    st.session_state["linea_limpieza_profunda"] = int(linea.tiempo_limpieza_profunda_min or 0)
    st.session_state["linea_flush"] = int(linea.tiempo_flush_min or 0)
    st.session_state["linea_observaciones"] = linea.observaciones or ""


def _save_linea() -> None:
    try:
        linea = Linea(
            id_linea=st.session_state.get("linea_edit_id"),
            codigo_linea=st.session_state["linea_codigo"].strip().upper(),
            nombre_linea=st.session_state["linea_nombre"].strip(),
            tonelaje_batch=float(st.session_state["linea_tonelaje_batch"]),
            capacidad_tn_hora=(
                float(st.session_state["linea_capacidad"])
                if float(st.session_state["linea_capacidad"]) > 0
                else None
            ),
            activo=bool(st.session_state["linea_activa"]),
            tiempo_limpieza_corta_min=int(st.session_state["linea_limpieza_corta"]),
            tiempo_limpieza_profunda_min=int(st.session_state["linea_limpieza_profunda"]),
            tiempo_flush_min=int(st.session_state["linea_flush"]),
            observaciones=st.session_state["linea_observaciones"].strip() or None,
        )

        if linea.id_linea is None:
            existente = LineasRepository.get_by_codigo(linea.codigo_linea)
            if existente is not None:
                st.error("Ya existe una línea con ese código.")
                return
            LineasRepository.create(linea)
            st.success("Línea creada correctamente.")
        else:
            existente = LineasRepository.get_by_codigo(linea.codigo_linea)
            if existente is not None and existente.id_linea != linea.id_linea:
                st.error("Ya existe otra línea con ese código.")
                return
            actualizado = LineasRepository.update(linea)
            if actualizado:
                st.success("Línea actualizada correctamente.")
            else:
                st.warning("No se realizaron cambios.")

        _reset_linea_form()

    except Exception as exc:
        st.error(f"Error al guardar la línea: {exc}")


def render_lineas() -> None:
    st.title("🏭 Líneas")
    st.write("Crear, listar y editar líneas o mezcladoras.")

    if "linea_edit_id" not in st.session_state:
        _reset_linea_form()

    with st.form("form_linea", clear_on_submit=False):
        st.subheader("Formulario de línea")

        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Código", key="linea_codigo")
            st.text_input("Nombre", key="linea_nombre")
            st.number_input(
                "Tonelaje por batch",
                min_value=0.1,
                value=float(st.session_state["linea_tonelaje_batch"]),
                step=0.1,
                key="linea_tonelaje_batch",
            )
            st.checkbox("Activa", key="linea_activa")

        with c2:
            st.number_input(
                "Capacidad tn/hora",
                min_value=0.0,
                value=float(st.session_state["linea_capacidad"]),
                step=0.1,
                key="linea_capacidad",
            )
            st.number_input(
                "Limpieza corta (min)",
                min_value=0,
                value=int(st.session_state["linea_limpieza_corta"]),
                step=1,
                key="linea_limpieza_corta",
            )
            st.number_input(
                "Limpieza profunda (min)",
                min_value=0,
                value=int(st.session_state["linea_limpieza_profunda"]),
                step=1,
                key="linea_limpieza_profunda",
            )
            st.number_input(
                "Flush (min)",
                min_value=0,
                value=int(st.session_state["linea_flush"]),
                step=1,
                key="linea_flush",
            )

        st.text_area("Observaciones", key="linea_observaciones")

        c1, c2 = st.columns(2)
        guardar = c1.form_submit_button("Guardar")
        limpiar = c2.form_submit_button("Limpiar formulario")

        if guardar:
            _save_linea()

        if limpiar:
            _reset_linea_form()
            st.rerun()

    st.markdown("---")
    st.subheader("Listado de líneas")

    lineas = LineasRepository.list_all(include_inactive=True)

    if not lineas:
        st.info("No hay líneas registradas.")
        return

    for linea in lineas:
        with st.expander(f"{linea.codigo_linea} - {linea.nombre_linea}"):
            st.write(f"**Tonelaje batch:** {linea.tonelaje_batch}")
            st.write(f"**Capacidad tn/hora:** {linea.capacidad_tn_hora or '-'}")
            st.write(
                f"**Tiempos de limpieza:** corta={linea.tiempo_limpieza_corta_min or 0} min, "
                f"profunda={linea.tiempo_limpieza_profunda_min or 0} min, "
                f"flush={linea.tiempo_flush_min or 0} min"
            )
            st.write(f"**Activa:** {'Sí' if linea.activo else 'No'}")
            st.write(f"**Observaciones:** {linea.observaciones or '-'}")

            c1, c2 = st.columns(2)
            if c1.button("Editar", key=f"edit_linea_{linea.id_linea}"):
                _load_linea_to_form(linea)
                st.rerun()

            if c2.button("Desactivar", key=f"deact_linea_{linea.id_linea}"):
                if linea.activo:
                    LineasRepository.deactivate(linea.id_linea)
                    st.success("Línea desactivada.")
                    st.rerun()
                else:
                    st.info("La línea ya está desactivada.")
