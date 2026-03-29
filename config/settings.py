from __future__ import annotations

from pathlib import Path

# =========================================================
# RUTAS BASE DEL PROYECTO
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

# =========================================================
# ARCHIVOS PRINCIPALES
# =========================================================
DB_PATH = DATABASE_DIR / "app.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"

# =========================================================
# EXPORTACIÓN
# =========================================================
DEFAULT_EXPORT_FILENAME = "secuencia_produccion.xlsx"
DEFAULT_EXPORT_PATH = EXPORTS_DIR / DEFAULT_EXPORT_FILENAME

# =========================================================
# CONFIGURACIÓN GENERAL MVP
# =========================================================
APP_NAME = "Premix Scheduler"
APP_VERSION = "0.1.0"
DEBUG = True

# =========================================================
# FORMATOS DE FECHA
# =========================================================
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# =========================================================
# VALORES POR DEFECTO
# =========================================================
DEFAULT_ESTADO_OP = "PENDIENTE"
DEFAULT_ESTADO_INICIAL_LINEA = "LIMPIA"

# =========================================================
# OPCIONES DE NEGOCIO MVP
# =========================================================
ACCIONES_TRANSICION = (
    "PERMITIDO",
    "PERMITIDO_CON_LIMPIEZA",
    "PERMITIDO_CON_FLUSH",
    "PROHIBIDO",
)

TIPOS_REGISTRO_SECUENCIA = (
    "PRODUCCION",
    "LIMPIEZA",
    "FLUSH",
)

ESTADOS_OP = (
    "PENDIENTE",
    "PLANIFICADA",
    "CANCELADA",
)

ESTADOS_INICIALES_LINEA = (
    "LIMPIA",
    "CON_PRODUCTO",
)

# =========================================================
# JERARQUÍAS DE NEGOCIO
# =========================================================
JERARQUIA_RIESGO = {
    "BAJO": 1,
    "MEDIO": 2,
    "ALTO": 3,
    "CRITICO": 4,
}

JERARQUIA_LIMPIEZA = {
    "NINGUNA": 0,
    "CORTA": 1,
    "FLUSH": 2,
    "PROFUNDA": 3,
}

JERARQUIA_CATEGORIAS = {
    "BASE": 1,
    "MINERAL": 2,
    "ALTA_RESTRICCION": 3,
    "COCCIDIOSTATO": 4,
    "MEDICADO": 5,
}

# =========================================================
# PARÁMETROS DEL SECUENCIADOR MVP
# =========================================================
COSTO_TRANSICION_PERMITIDA = 0
COSTO_LIMPIEZA_CORTA = 30
COSTO_FLUSH = 50
COSTO_LIMPIEZA_PROFUNDA = 100
COSTO_TRANSICION_PROHIBIDA = 999999

# =========================================================
# FUNCIÓN AUXILIAR
# =========================================================
def ensure_directories() -> None:
    """
    Crea las carpetas principales del proyecto si no existen.
    """
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
