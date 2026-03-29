from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION
from database.connection import initialize_database
from ui.pages.inicio import render_inicio
from ui.pages.secuenciador import render_secuenciador
from ui.pages.datos_demo import render_datos_demo


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
            "Secuenciador",
            "Datos demo",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"{APP_NAME} v{APP_VERSION}")

    if page == "Inicio":
        render_inicio()

    elif page == "Secuenciador":
        render_secuenciador()

    elif page == "Datos demo":
        render_datos_demo()


if __name__ == "__main__":
    main()
