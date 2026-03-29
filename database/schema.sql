PRAGMA foreign_keys = ON;

-- =========================================================
-- TABLA: insumos
-- Catálogo maestro de insumos
-- =========================================================
CREATE TABLE IF NOT EXISTS insumos (
    id_insumo INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_insumo TEXT NOT NULL UNIQUE,
    nombre_insumo TEXT NOT NULL,
    categoria_riesgo TEXT NOT NULL,
    nivel_riesgo TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    limpieza_sugerida TEXT,
    es_critico INTEGER NOT NULL DEFAULT 0 CHECK (es_critico IN (0,1)),
    observaciones TEXT
);

-- =========================================================
-- TABLA: formulas
-- Cabecera de fórmulas
-- =========================================================
CREATE TABLE IF NOT EXISTS formulas (
    id_formula INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_formula TEXT NOT NULL,
    nombre_formula TEXT NOT NULL,
    version_formula TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    observaciones TEXT,
    UNIQUE (codigo_formula, version_formula)
);

-- =========================================================
-- TABLA: formula_detalle
-- Relación fórmula - insumo
-- =========================================================
CREATE TABLE IF NOT EXISTS formula_detalle (
    id_formula_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    id_formula INTEGER NOT NULL,
    id_insumo INTEGER NOT NULL,
    cantidad REAL NOT NULL CHECK (cantidad > 0),
    unidad TEXT NOT NULL,
    observaciones TEXT,
    FOREIGN KEY (id_formula) REFERENCES formulas(id_formula),
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo),
    UNIQUE (id_formula, id_insumo)
);

-- =========================================================
-- TABLA: lineas
-- Mezcladoras o líneas
-- =========================================================
CREATE TABLE IF NOT EXISTS lineas (
    id_linea INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_linea TEXT NOT NULL UNIQUE,
    nombre_linea TEXT NOT NULL,
    tonelaje_batch REAL NOT NULL CHECK (tonelaje_batch > 0),
    capacidad_tn_hora REAL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    tiempo_limpieza_corta_min INTEGER,
    tiempo_limpieza_profunda_min INTEGER,
    tiempo_flush_min INTEGER,
    observaciones TEXT
);

-- =========================================================
-- TABLA: tipos_limpieza
-- Catálogo de limpiezas posibles
-- =========================================================
CREATE TABLE IF NOT EXISTS tipos_limpieza (
    id_limpieza INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_limpieza TEXT NOT NULL UNIQUE,
    nombre_limpieza TEXT NOT NULL,
    duracion_min INTEGER,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    descripcion TEXT
);

-- =========================================================
-- TABLA: reglas_riesgo
-- Matriz de transición entre categorías
-- =========================================================
CREATE TABLE IF NOT EXISTS reglas_riesgo (
    id_regla INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_origen TEXT NOT NULL,
    categoria_destino TEXT NOT NULL,
    accion TEXT NOT NULL,
    id_limpieza INTEGER,
    prioridad INTEGER NOT NULL DEFAULT 1,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    observaciones TEXT,
    FOREIGN KEY (id_limpieza) REFERENCES tipos_limpieza(id_limpieza),
    UNIQUE (categoria_origen, categoria_destino, prioridad)
);

-- =========================================================
-- TABLA: perfil_riesgo_formula
-- Perfil calculado de riesgo de fórmula
-- =========================================================
CREATE TABLE IF NOT EXISTS perfil_riesgo_formula (
    id_perfil INTEGER PRIMARY KEY AUTOINCREMENT,
    id_formula INTEGER NOT NULL UNIQUE,
    categoria_dominante TEXT NOT NULL,
    nivel_riesgo_resultante TEXT NOT NULL,
    limpieza_sugerida TEXT,
    contiene_critico INTEGER NOT NULL DEFAULT 0 CHECK (contiene_critico IN (0,1)),
    detalle_riesgo TEXT,
    fecha_calculo TEXT NOT NULL,
    FOREIGN KEY (id_formula) REFERENCES formulas(id_formula)
);

-- =========================================================
-- TABLA: estado_inicial_lineas
-- Estado inicial configurable de cada línea
-- =========================================================
CREATE TABLE IF NOT EXISTS estado_inicial_lineas (
    id_estado_inicial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_linea INTEGER NOT NULL UNIQUE,
    estado_inicial_tipo TEXT NOT NULL,
    id_formula_anterior INTEGER,
    id_limpieza_ultima INTEGER,
    observaciones TEXT,
    FOREIGN KEY (id_linea) REFERENCES lineas(id_linea),
    FOREIGN KEY (id_formula_anterior) REFERENCES formulas(id_formula),
    FOREIGN KEY (id_limpieza_ultima) REFERENCES tipos_limpieza(id_limpieza)
);

-- =========================================================
-- TABLA: ordenes_produccion
-- Órdenes de producción a planificar
-- =========================================================
CREATE TABLE IF NOT EXISTS ordenes_produccion (
    id_op INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_op TEXT NOT NULL UNIQUE,
    fecha_op TEXT NOT NULL,
    id_formula INTEGER NOT NULL,
    toneladas REAL NOT NULL CHECK (toneladas > 0),
    prioridad INTEGER NOT NULL DEFAULT 0,
    fecha_compromiso TEXT,
    id_linea_preferida INTEGER,
    estado TEXT NOT NULL DEFAULT 'PENDIENTE',
    observaciones TEXT,
    FOREIGN KEY (id_formula) REFERENCES formulas(id_formula),
    FOREIGN KEY (id_linea_preferida) REFERENCES lineas(id_linea)
);

-- =========================================================
-- TABLA: secuencias
-- Cabecera de cada corrida de planificación
-- =========================================================
CREATE TABLE IF NOT EXISTS secuencias (
    id_secuencia INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_generacion TEXT NOT NULL,
    criterio_planificacion TEXT,
    version_matriz TEXT,
    observaciones TEXT
);

-- =========================================================
-- TABLA: detalle_secuencia
-- Resultado detallado por línea
-- =========================================================
CREATE TABLE IF NOT EXISTS detalle_secuencia (
    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    id_secuencia INTEGER NOT NULL,
    id_linea INTEGER NOT NULL,
    posicion INTEGER NOT NULL,
    tipo_registro TEXT NOT NULL,
    id_op INTEGER,
    id_limpieza INTEGER,
    categoria_origen TEXT,
    categoria_destino TEXT,
    accion_transicion TEXT,
    justificacion TEXT,
    editado_manual INTEGER NOT NULL DEFAULT 0 CHECK (editado_manual IN (0,1)),
    FOREIGN KEY (id_secuencia) REFERENCES secuencias(id_secuencia),
    FOREIGN KEY (id_linea) REFERENCES lineas(id_linea),
    FOREIGN KEY (id_op) REFERENCES ordenes_produccion(id_op),
    FOREIGN KEY (id_limpieza) REFERENCES tipos_limpieza(id_limpieza),
    UNIQUE (id_secuencia, id_linea, posicion)
);

-- =========================================================
-- ÍNDICES
-- =========================================================
CREATE INDEX IF NOT EXISTS idx_formula_detalle_formula
    ON formula_detalle(id_formula);

CREATE INDEX IF NOT EXISTS idx_formula_detalle_insumo
    ON formula_detalle(id_insumo);

CREATE INDEX IF NOT EXISTS idx_ordenes_formula
    ON ordenes_produccion(id_formula);

CREATE INDEX IF NOT EXISTS idx_ordenes_estado
    ON ordenes_produccion(estado);

CREATE INDEX IF NOT EXISTS idx_detalle_secuencia_secuencia
    ON detalle_secuencia(id_secuencia);

CREATE INDEX IF NOT EXISTS idx_detalle_secuencia_linea
    ON detalle_secuencia(id_linea);

CREATE INDEX IF NOT EXISTS idx_reglas_riesgo_origen_destino
    ON reglas_riesgo(categoria_origen, categoria_destino);
