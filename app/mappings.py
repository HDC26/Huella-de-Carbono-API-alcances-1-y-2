"""
Mapeos EXPLÍCITOS de qué hojas/columnas de cada xlsx contienen factores de
emisión reales, listos para insertar en la tabla `factores_emision`.

*** Por qué esto no es automático ***
Las planillas del corpus (Factor de Emisión.xlsx, herramientas del GHG
Protocol, ICE DB, etc.) tienen estructuras completamente distintas entre sí,
y varias hojas dentro del mismo archivo NO son tablas de factores (son UI de
calculadora, notas, versionado, etc.). Adivinar columnas automáticamente
arriesga cargar un dato incorrecto como si fuera un factor de emisión válido
-- inaceptable para un sistema que se usa en auditoría.

Por eso: cada hoja que sí es una tabla de factores se declara acá, a mano,
una sola vez. `ingest_xlsx.py` sólo ejecuta lo que está declarado en
MAPEOS_HOJAS_VALIDAS.

*** Cómo agregar un mapeo nuevo ***
1. Corré: python -m app.inspeccionar_xlsx "archivo.xlsx"                (ver hojas)
2. Corré: python -m app.inspeccionar_xlsx "archivo.xlsx" --hoja "X"     (ver filas/columnas)
3. Agregá una entrada a MAPEOS_HOJAS_VALIDAS con los índices de columna
   correctos (0-indexado) y la fila donde empiezan los datos.
"""

# Cada entrada define cómo leer UNA hoja de UN archivo.
# columnas: índice (0-indexado) de cada dato dentro de la hoja.
# fila_inicio: primera fila de datos (1-indexado, salteando encabezados).
MAPEOS_HOJAS_VALIDAS = [
    {
        "archivo": "Stationary_combustion_tool_Version4-2.xlsx",
        "hoja": "CO2 EFs",
        "alcance": "alcance_1",
        "categoria": "combustion_fija",
        "fila_inicio": 4,          # AJUSTAR tras inspeccionar la hoja real
        "columnas": {
            "nombre_factor": 0,     # ej: tipo de combustible
            "valor": 2,             # ej: valor numérico del factor
            "unidad": 3,
            "gas": None,            # fijo: se completa como "CO2" abajo
            "fuente": None,         # fijo: "GHG Protocol - Stationary Combustion Tool v4.2"
        },
        "gas_fijo": "CO2",
        "fuente_fija": "GHG Protocol - Stationary Combustion Tool v4.2",
        "anio_fijo": 2024,
    },
    {
        "archivo": "Stationary_combustion_tool_Version4-2.xlsx",
        "hoja": "Tier 1 CH4  EFs",
        "alcance": "alcance_1",
        "categoria": "combustion_fija",
        "fila_inicio": 4,          # AJUSTAR tras inspeccionar la hoja real
        "columnas": {
            "nombre_factor": 0,
            "valor": 2,
            "unidad": 3,
            "gas": None,
            "fuente": None,
        },
        "gas_fijo": "CH4",
        "fuente_fija": "GHG Protocol - Stationary Combustion Tool v4.2",
        "anio_fijo": 2024,
    },
    {
        "archivo": "Stationary_combustion_tool_Version4-2.xlsx",
        "hoja": "Tier 1 N2O  EFs",
        "alcance": "alcance_1",
        "categoria": "combustion_fija",
        "fila_inicio": 4,          # AJUSTAR tras inspeccionar la hoja real
        "columnas": {
            "nombre_factor": 0,
            "valor": 2,
            "unidad": 3,
            "gas": None,
            "fuente": None,
        },
        "gas_fijo": "N2O",
        "fuente_fija": "GHG Protocol - Stationary Combustion Tool v4.2",
        "anio_fijo": 2024,
    },

    # NOTA: "Factor de Emision.xlsx" queda pendiente -- es una matriz de
    # generación/consumo eléctrico, no una tabla de factores directa.
    # Requiere una decisión de ingeniería (¿derivar factor = emisiones/generación,
    # o buscar el factor de red ya publicado en otra fuente del corpus, ej.
    # ghg-emission-factors-hub-2024.pdf?) antes de mapearla acá.
    # Categoría relevante cuando se resuelva: alcance = "alcance_2",
    # categoria = "energia_electrica".
]
