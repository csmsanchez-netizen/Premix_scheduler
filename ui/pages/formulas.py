from __future__ import annotations

import streamlit as st

from models.formula import Formula
from models.formula_detalle import FormulaDetalle
from repositories.formulas_repository import FormulasRepository
from repositories.insumos_repository import InsumosRepository
from services.riesgo_service import RiesgoService


def _reset_formula_form() -> None:
    st.session_state["formula_edit_id"] = None
    st.session_state["formula_codigo"] = ""
    st.session_state["formula_nombre"] = ""
    st.session_state["formula_version"] = "1"
    st.session_state["formula_activa"] = True
    st.session_state["formula_observaciones"] = ""


def _load_formula_to_form(formula: Formula) -> None:
    st.session_state["formula_edit_id"] = formula.id_formula
    st.session_state["formula_codigo"] = formula.codigo_formula
    st.session_state["formula_nombre"] = formula.nombre_formula
    st.session_state["formula_version"] = formula.version_formula
    st.session_state["formula_activa"] = formula.activo
    st.session_state["formula_observaciones"] = formula.observaciones or ""


def _save_formula() -> None:
    try:
        formula = Formula(
            id_formula=st.session_state.get("formula_edit_id"),
            codigo_formula=st.session_state["formula_codigo"].strip().upper(),
            nombre_formula=st.session_state["formula_nombre"].strip(),
            version_formula=st.session_state["formula_version"].strip(),
            activo=bool(st.session_state["formula_activa"]),
            observaciones=st.session_state["formula_observaciones"].strip() or None,
        )

        if formula.id_formula is None:
            existente = FormulasRepository.get_by_codigo_version(
                formula.codigo_formula,
                formula.version_formula,
            )
            if existente is not None:
                st.error("Ya existe una fórmula con ese código y versión.")
                return

            nuevo_id = FormulasRepository.create(formula)
            st.session_state["formula_edit_id"] = nuevo_id
            st.success("Fórmula creada correctamente.")
        else:
            existente = FormulasRepository.get_by_codigo_version(
                formula.codigo_formula,
                formula.version_formula,
            )
            if existente is not None and existente.id_formula != formula.id_formula:
                st.error("Ya existe otra fórmula con ese código y versión.")
                return

            actualizado = FormulasRepository.update(formula)
            if actualizado:
                st.success("Fórmula actualizada correctamente.")
            else:
                st.warning("No se realizaron cambios.")

    except Exception as exc:
        st.error(f"Error al guardar la fórmula: {exc}")


def _guardar_detalle_formula(id_formula: int) -> None:
    insumo_ids = st.session_state.get("detalle_insumo_id", [])
    cantidades = st.session_state.get("detalle_cantidad", [])
    unidades = st.session_state.get("detalle_unidad", [])
    observaciones = st.session_state.get("detalle_observacion", [])

    try:
        detalles: list[FormulaDetalle] = []

        for i, id_insumo in enumerate(insumo_ids):
            if not id_insumo:
                continue

            cantidad = float(cantidades[i]) if i < len(cantidades) else 0
            unidad = unidades[i].strip() if i < len(unidades) else ""
            obs = observaciones[i].strip() if i < len(observaciones) else None

            detalle = FormulaDetalle(
                id_formula_detalle=None,
                id_formula=id_formula,
                id_insumo=int(id_insumo),
                cantidad=cantidad,
                unidad=unidad,
                observaciones=obs or None,
            )
            detalles.append(detalle)

        if not detalles:
            st.warning("Debes cargar al menos una fila válida en el detalle.")
            return

        FormulasRepository.replace_detalle(id_formula, detalles)
        st.success("Detalle de fórmula guardado correctamente.")

    except Exception as exc:
        st.error(f"Error al guardar detalle de fórmula: {exc}")


def render_formulas() -> None:
    st.title("🧪 Fórmulas")
    st.write("Crear, listar y editar fórmulas y su composición.")

    if "formula_edit_id" not in st.session_state:
        _reset_formula_form()

    with st.form("form_formula", clear_on_submit=False):
        st.subheader("Cabecera de fórmula")

        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Código", key="formula_codigo")
            st.text_input("Nombre", key="formula_nombre")
        with c2:
            st.text_input("Versión", key="formula_version")
            st.checkbox("Activa", key="formula_activa")

        st.text_area("Observaciones", key="formula_observaciones")

        c1, c2 = st.columns(2)
        guardar = c1.form_submit_button("Guardar cabecera")
        limpiar = c2.form_submit_button("Limpiar formulario")

        if guardar:
            _save_formula()

        if limpiar:
            _reset_formula_form()
            st.rerun()

    st.markdown("---")
    st.subheader("Detalle de fórmula")

    formula_id = st.session_state.get("formula_edit_id")
    insumos = InsumosRepository.list_all(include_inactive=False)

    if formula_id is None:
        st.info("Primero guarda la cabecera de la fórmula para poder cargar su detalle.")
    elif not insumos:
        st.warning("No hay insumos activos para asociar.")
    else:
        opciones_insumos = {
            f"{insumo.codigo_insumo} - {insumo.nombre_insumo}": insumo.id_insumo
            for insumo in insumos
        }
        labels = [""] + list(opciones_insumos.keys())

        detalles_existentes = FormulasRepository.list_detalle_by_formula(formula_id)
        filas = max(5, len(detalles_existentes))

        default_labels = []
        default_cantidades = []
        default_unidades = []
        default_observaciones = []

        id_to_label = {v: k for k, v in opciones_insumos.items()}

        for detalle in detalles_existentes:
            default_labels.append(id_to_label.get(detalle.id_insumo, ""))
            default_cantidades.append(float(detalle.cantidad))
            default_unidades.append(detalle.unidad)
            default_observaciones.append(detalle.observaciones or "")

        while len(default_labels) < filas:
            default_labels.append("")
            default_cantidades.append(0.0)
            default_unidades.append("kg")
            default_observaciones.append("")

        with st.form("form_detalle_formula", clear_on_submit=False):
            seleccionados_ids = []
            cantidades = []
            unidades = []
            observaciones = []

            for i in range(filas):
                c1, c2, c3, c4 = st.columns([4, 2, 2, 4])
                with c1:
                    label = st.selectbox(
                        f"Insumo {i + 1}",
                        labels,
                        index=labels.index(default_labels[i]) if default_labels[i] in labels else 0,
                        key=f"detalle_label_{i}",
                    )
                with c2:
                    cantidad = st.number_input(
                        f"Cantidad {i + 1}",
                        min_value=0.0,
                        value=float(default_cantidades[i]),
                        step=1.0,
                        key=f"detalle_cantidad_{i}",
                    )
                with c3:
                    unidad = st.text_input(
                        f"Unidad {i + 1}",
                        value=default_unidades[i],
                        key=f"detalle_unidad_{i}",
                    )
                with c4:
                    obs = st.text_input(
                        f"Obs {i + 1}",
                        value=default_observaciones[i],
                        key=f"detalle_obs_{i}",
                    )

                seleccionados_ids.append(opciones_insumos.get(label))
                cantidades.append(cantidad)
                unidades.append(unidad)
                observaciones.append(obs)

            st.session_state["detalle_insumo_id"] = seleccionados_ids
            st.session_state["detalle_cantidad"] = cantidades
            st.session_state["detalle_unidad"] = unidades
            st.session_state["detalle_observacion"] = observaciones

            guardar_detalle = st.form_submit_button("Guardar detalle")
            if guardar_detalle:
                _guardar_detalle_formula(formula_id)

        if st.button("Calcular perfil de riesgo"):
            try:
                perfil = RiesgoService.calcular_perfil_formula(formula_id)
                st.success("Perfil calculado correctamente.")
                st.json(perfil.to_dict())
            except Exception as exc:
                st.error(f"No se pudo calcular el perfil: {exc}")

    st.markdown("---")
    st.subheader("Listado de fórmulas")

    formulas = FormulasRepository.list_all(include_inactive=True)

    if not formulas:
        st.info("No hay fórmulas registradas.")
        return

    for formula in formulas:
        with st.expander(
            f"{formula.codigo_formula} v{formula.version_formula} - {formula.nombre_formula}"
        ):
            st.write(f"**Activa:** {'Sí' if formula.activo else 'No'}")
            st.write(f"**Observaciones:** {formula.observaciones or '-'}")

            detalles = FormulasRepository.list_detalle_by_formula(formula.id_formula)
            if detalles:
                st.write("**Detalle:**")
                for detalle in detalles:
                    insumo = InsumosRepository.get_by_id(detalle.id_insumo)
                    nombre_insumo = (
                        f"{insumo.codigo_insumo} - {insumo.nombre_insumo}"
                        if insumo
                        else f"Insumo {detalle.id_insumo}"
                    )
                    st.write(
                        f"- {nombre_insumo}: {detalle.cantidad} {detalle.unidad}"
                    )
            else:
                st.info("Sin detalle de fórmula.")

            c1, c2 = st.columns(2)
            if c1.button("Editar", key=f"edit_formula_{formula.id_formula}"):
                _load_formula_to_form(formula)
                st.rerun()

            if c2.button("Desactivar", key=f"deact_formula_{formula.id_formula}"):
                if formula.activo:
                    FormulasRepository.deactivate(formula.id_formula)
                    st.success("Fórmula desactivada.")
                    st.rerun()
                else:
                    st.info("La fórmula ya está desactivada.")
