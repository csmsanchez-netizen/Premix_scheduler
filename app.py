from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION
from database.connection import initialize_database
from ui.pages.datos_demo import render_datos_demo
from ui.pages.formulas import render_formulas
from ui.pages.inicio import render_inicio
from ui.pages.insumos import render_insumos
from ui.pages.lineas import render_lineas
from ui.pages.secuenciador import render_secuenciador


def setup_app() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_database()


def main() -> None:
    setup_app()

    st.sidebar.title("Menú")
    page = st.sidebar.radio(
        "Ir a:",
        options=[
            "Inicio",
            "Datos demo",
            "Insumos",
            "Fórmulas",
            "Líneas",
            "Secuenciador",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"{APP_NAME} v{APP_VERSION}")

    if page == "Inicio":
        render_inicio()
    elif page == "Datos demo":
        render_datos_demo()
    elif page == "Insumos":
        render_insumos()
    elif page == "Fórmulas":
        render_formulas()
    elif page == "Líneas":
        render_lineas()
    elif page == "Secuenciador":
        render_secuenciador()


if __name__ == "__main__":
    main()
