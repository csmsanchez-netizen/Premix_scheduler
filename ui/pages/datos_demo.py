from __future__ import annotations

import streamlit as st

from database.seed import main as seed_main
from database.connection import test_connection


def render_datos_demo() -> None:
    st.title("🧪 Cargar datos de prueba")
    st.write(
        "Esta herramienta permite cargar un conjunto de datos demo para probar "
        "el sistema rápidamente."
    )

    st.markdown("---")

    if not test_connection():
        st.error("No hay conexión a la base de datos.")
        return

    st.info(
        "Esto cargará insumos, fórmulas, líneas, reglas y órdenes de ejemplo.\n\n"
        "Puedes ejecutarlo varias veces sin duplicar datos (usa INSERT OR IGNORE)."
    )

    if st.button("Cargar datos demo", type="primary"):
        try:
            seed_main()
            st.success("Datos de prueba cargados correctamente.")
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")

    st.markdown("---")
    st.caption("Recomendado ejecutar esto al desplegar en Streamlit Cloud por primera vez.")
