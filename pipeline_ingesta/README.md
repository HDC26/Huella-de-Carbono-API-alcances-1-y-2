# Pipeline de Ingesta — Huella de Carbono (Corpus v1: Alcance 1 y 2)

## Qué hace

1. **`ingest_pdf.py`** — Extrae texto de los PDFs del corpus (fundamentación
   + guías), lo trocea en chunks con página/sección, genera embeddings y los
   guarda en Supabase (pgvector) para búsqueda semántica.
2. **`ingest_xlsx.py`** — Carga factores de emisión estructurados desde las
   hojas de xlsx que vos mapeaste explícitamente en `app/mappings.py`
   (búsqueda exacta, no semántica — ver por qué en ese archivo).

## Paso 1 — Crear el proyecto en Supabase

1. Creá un proyecto en https://supabase.com (plan gratuito alcanza para el MVP).
2. Andá a **SQL Editor** y ejecutá el contenido de `sql/schema.sql` completo.
   Esto habilita pgvector y crea las tablas `documentos`, `chunks`,
   `factores_emision` y la función de búsqueda `buscar_chunks_similares`.
3. Andá a **Project Settings > Database > Connection string** y copiá la
   cadena de conexión (modo "URI").

## Paso 2 — Configurar el entorno local

```bash
cd pipeline_ingesta
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env con:
#   - DATABASE_URL   (la cadena de conexión de Supabase)
#   - OPENAI_API_KEY (tu API key de OpenAI)
#   - CORPUS_VERSION (ej: v1_2026-08-17)
#   - CORPUS_PATH    (ruta a la carpeta corpus_v1/)
```

Copiá también la carpeta `corpus_v1/` (la que ya curamos: fundamentación,
factores generales, combustión fija) al lado de este proyecto, o ajustá
`CORPUS_PATH` en `.env` para que apunte a donde la tengas.

## Paso 3 — Ingestar los PDFs (texto + embeddings)

```bash
python -m app.ingest_pdf
```

Esto recorre `00_fundamentacion/`, `01_factores_generales/` y
`02_alcance1_combustion_fija/`, extrae texto página por página, lo trocea y
sube los embeddings a la tabla `chunks`. Es idempotente: si corrés el
comando de nuevo con la misma `CORPUS_VERSION`, no duplica documentos ya
cargados.

## Paso 4 — Mapear y cargar los factores de emisión (xlsx)

Este paso requiere tu criterio de ingeniero antes de automatizar nada:

```bash
# 1. Ver qué hojas tiene un archivo
python -m app.inspeccionar_xlsx "corpus_v1/02_alcance1_combustion_fija/Stationary_combustion_tool_Version4-2.xlsx"

# 2. Ver el contenido real de una hoja candidata
python -m app.inspeccionar_xlsx "corpus_v1/02_alcance1_combustion_fija/Stationary_combustion_tool_Version4-2.xlsx" --hoja "CO2 EFs" --filas 20

# 3. Ajustar/completar app/mappings.py con los índices de columna correctos
#    (ya dejé 3 mapeos de ejemplo para el archivo de combustión fija,
#     pero los índices de columna hay que confirmarlos con el paso 2)

# 4. Correr la ingesta de factores
python -m app.ingest_xlsx
```

**Pendiente importante**: `Factor de Emision.xlsx` no es una tabla de
factores lista para usar — es una matriz de generación/consumo eléctrico
mensual. Antes de mapearla necesitás decidir si el factor de red (Alcance 2)
sale de derivarlo de esos datos, o de otra fuente del corpus como
`ghg-emission-factors-hub-2024.pdf`. Quedó documentado en `app/mappings.py`.

## Paso 5 — Verificar en Supabase

En el **Table Editor** de Supabase deberías ver filas en `documentos`,
`chunks` (con `pagina` y `embedding` poblados) y `factores_emision` (con
`archivo_origen`, `hoja` y `fila` — esa es tu trazabilidad).

## Siguiente paso (no incluido acá)

Con los datos ya en Supabase, el siguiente componente es la **API de
consulta** (FastAPI) que expone `/consultar-factor` y `/calcular`, usando
`buscar_chunks_similares()` para las fórmulas y un lookup directo en
`factores_emision` para los valores numéricos. Eso es lo que Base44 va a
llamar vía backend functions.
