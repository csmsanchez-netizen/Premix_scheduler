from __future__ import annotations

from database.connection import initialize_database, get_connection


def seed_tipos_limpieza() -> None:
    registros = [
        ("NINGUNA", "Ninguna", 0, 1, "Sin limpieza requerida"),
        ("CORTA", "Limpieza corta", 15, 1, "Limpieza corta estándar"),
        ("FLUSH", "Flush", 20, 1, "Flush con material de arrastre"),
        ("PROFUNDA", "Limpieza profunda", 45, 1, "Limpieza profunda obligatoria"),
    ]

    query = """
        INSERT OR IGNORE INTO tipos_limpieza (
            codigo_limpieza,
            nombre_limpieza,
            duracion_min,
            activo,
            descripcion
        )
        VALUES (?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, registros)
        conn.commit()


def seed_insumos() -> None:
    registros = [
        ("MP001", "Carbonato de calcio", "BASE", "BAJO", 1, "NINGUNA", 0, "Insumo base"),
        ("MP002", "Sulfato de cobre", "MINERAL", "MEDIO", 1, "CORTA", 0, "Mineral"),
        ("MP003", "Aditivo medicado X", "MEDICADO", "CRITICO", 1, "PROFUNDA", 1, "Crítico"),
        ("MP004", "Coccidiostato Y", "COCCIDIOSTATO", "ALTO", 1, "FLUSH", 1, "Uso controlado"),
    ]

    query = """
        INSERT OR IGNORE INTO insumos (
            codigo_insumo,
            nombre_insumo,
            categoria_riesgo,
            nivel_riesgo,
            activo,
            limpieza_sugerida,
            es_critico,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, registros)
        conn.commit()


def seed_formulas() -> None:
    registros = [
        ("F001", "Fórmula Base", "1", 1, "Fórmula simple"),
        ("F002", "Fórmula Mineral", "1", 1, "Incluye mineral"),
        ("F003", "Fórmula Medicada", "1", 1, "Incluye medicado"),
        ("F004", "Fórmula Coccidiostato", "1", 1, "Incluye coccidiostato"),
    ]

    query = """
        INSERT OR IGNORE INTO formulas (
            codigo_formula,
            nombre_formula,
            version_formula,
            activo,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, registros)
        conn.commit()


def get_formula_id(codigo_formula: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id_formula FROM formulas WHERE codigo_formula = ? AND version_formula = '1'",
            (codigo_formula,),
        ).fetchone()
    return row["id_formula"] if row else None


def get_insumo_id(codigo_insumo: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id_insumo FROM insumos WHERE codigo_insumo = ?",
            (codigo_insumo,),
        ).fetchone()
    return row["id_insumo"] if row else None


def get_limpieza_id(codigo_limpieza: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id_limpieza FROM tipos_limpieza WHERE codigo_limpieza = ?",
            (codigo_limpieza,),
        ).fetchone()
    return row["id_limpieza"] if row else None


def seed_formula_detalle() -> None:
    detalles = []

    f001 = get_formula_id("F001")
    f002 = get_formula_id("F002")
    f003 = get_formula_id("F003")
    f004 = get_formula_id("F004")

    mp001 = get_insumo_id("MP001")
    mp002 = get_insumo_id("MP002")
    mp003 = get_insumo_id("MP003")
    mp004 = get_insumo_id("MP004")

    if f001 and mp001:
        detalles.append((f001, mp001, 100.0, "kg", "Base"))
    if f002 and mp001 and mp002:
        detalles.extend([
            (f002, mp001, 90.0, "kg", "Base"),
            (f002, mp002, 10.0, "kg", "Mineral"),
        ])
    if f003 and mp001 and mp003:
        detalles.extend([
            (f003, mp001, 95.0, "kg", "Base"),
            (f003, mp003, 5.0, "kg", "Medicado"),
        ])
    if f004 and mp001 and mp004:
        detalles.extend([
            (f004, mp001, 92.0, "kg", "Base"),
            (f004, mp004, 8.0, "kg", "Coccidiostato"),
        ])

    query = """
        INSERT OR IGNORE INTO formula_detalle (
            id_formula,
            id_insumo,
            cantidad,
            unidad,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, detalles)
        conn.commit()


def seed_lineas() -> None:
    registros = [
        ("L1", "Línea 1", 2.0, 8.0, 1, 15, 45, 20, "Mezcladora principal"),
        ("L2", "Línea 2", 5.0, 12.0, 1, 20, 50, 25, "Mezcladora secundaria"),
    ]

    query = """
        INSERT OR IGNORE INTO lineas (
            codigo_linea,
            nombre_linea,
            tonelaje_batch,
            capacidad_tn_hora,
            activo,
            tiempo_limpieza_corta_min,
            tiempo_limpieza_profunda_min,
            tiempo_flush_min,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, registros)
        conn.commit()


def seed_reglas_riesgo() -> None:
    corta = get_limpieza_id("CORTA")
    flush = get_limpieza_id("FLUSH")
    profunda = get_limpieza_id("PROFUNDA")

    registros = [
        ("BASE", "BASE", "PERMITIDO", None, 1, 1, "Libre"),
        ("BASE", "MINERAL", "PERMITIDO", None, 1, 1, "Libre"),
        ("MINERAL", "BASE", "PERMITIDO_CON_LIMPIEZA", corta, 1, 1, "Requiere limpieza corta"),
        ("BASE", "MEDICADO", "PERMITIDO", None, 1, 1, "Secuencia creciente"),
        ("MEDICADO", "BASE", "PERMITIDO_CON_LIMPIEZA", profunda, 1, 1, "Requiere limpieza profunda"),
        ("BASE", "COCCIDIOSTATO", "PERMITIDO", None, 1, 1, "Secuencia creciente"),
        ("COCCIDIOSTATO", "BASE", "PERMITIDO_CON_FLUSH", flush, 1, 1, "Requiere flush"),
        ("MEDICADO", "MINERAL", "PERMITIDO_CON_LIMPIEZA", profunda, 1, 1, "Requiere limpieza profunda"),
        ("MINERAL", "MEDICADO", "PERMITIDO", None, 1, 1, "Permitido"),
        ("COCCIDIOSTATO", "MEDICADO", "PROHIBIDO", None, 1, 1, "No permitido"),
    ]

    query = """
        INSERT OR IGNORE INTO reglas_riesgo (
            categoria_origen,
            categoria_destino,
            accion,
            id_limpieza,
            prioridad,
            activo,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, registros)
        conn.commit()


def seed_ordenes() -> None:
    f001 = get_formula_id("F001")
    f002 = get_formula_id("F002")
    f003 = get_formula_id("F003")
    f004 = get_formula_id("F004")

    registros = []
    if f001:
        registros.append(("OP001", "2026-03-29", f001, 4.0, 1, "2026-03-30", None, "PENDIENTE", "Base"))
    if f002:
        registros.append(("OP002", "2026-03-29", f002, 5.0, 2, "2026-03-30", None, "PENDIENTE", "Mineral"))
    if f003:
        registros.append(("OP003", "2026-03-29", f003, 3.0, 3, "2026-03-30", None, "PENDIENTE", "Medicada"))
    if f004:
        registros.append(("OP004", "2026-03-29", f004, 2.5, 2, "2026-03-30", None, "PENDIENTE", "Coccidiostato"))

    query = """
        INSERT OR IGNORE INTO ordenes_produccion (
            numero_op,
            fecha_op,
            id_formula,
            toneladas,
            prioridad,
            fecha_compromiso,
            id_linea_preferida,
            estado,
            observaciones
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as conn:
        conn.executemany(query, registros)
        conn.commit()


def main() -> None:
    initialize_database()
    seed_tipos_limpieza()
    seed_insumos()
    seed_formulas()
    seed_formula_detalle()
    seed_lineas()
    seed_reglas_riesgo()
    seed_ordenes()
    print("Datos de prueba cargados correctamente.")


if __name__ == "__main__":
    main()
