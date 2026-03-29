from __future__ import annotations

from database.connection import initialize_database, get_connection


def main() -> None:
    """
    Carga datos mínimos de prueba.
    """
    initialize_database()

    with get_connection() as conn:
        # Ejemplo mínimo: insertar un insumo si no existe
        conn.execute("""
            INSERT OR IGNORE INTO insumos (
                codigo_insumo,
                nombre_insumo,
                categoria_riesgo,
                nivel_riesgo,
                activo,
                limpieza_sugerida,
                es_critico
            )
            VALUES ('MP001', 'Insumo Demo', 'BASE', 'BAJO', 1, 'NINGUNA', 0)
        """)

        conn.commit()

    print("Datos demo cargados correctamente.")


if __name__ == "__main__":
    main()
