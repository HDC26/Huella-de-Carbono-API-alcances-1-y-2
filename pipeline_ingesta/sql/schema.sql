-- =============================================================
-- Esquema Supabase (Postgres + pgvector) - Huella de Carbono
-- Corpus v1: Alcance 1 y Alcance 2 únicamente
-- =============================================================

-- 1. Habilitar la extensión pgvector (una sola vez por proyecto)
create extension if not exists vector;

-- 2. Documentos fuente (metadatos de cada archivo del corpus)
create table if not exists documentos (
    id              uuid primary key default gen_random_uuid(),
    nombre_archivo  text not null,
    categoria       text not null,       -- 'fundamentacion' | 'factores_generales' | 'alcance1_combustion_fija'
    tipo            text not null,       -- 'pdf' | 'xlsx'
    version_corpus  text not null,       -- ej: 'v1_2026-08-17'
    hash_archivo    text,                -- para detectar si un archivo cambió entre versiones
    fecha_ingesta   timestamptz default now()
);

-- 3. Chunks de texto (para PDFs) con su embedding
create table if not exists chunks (
    id              uuid primary key default gen_random_uuid(),
    documento_id    uuid references documentos(id) on delete cascade,
    contenido       text not null,
    pagina          int,                 -- página de origen, para citación exacta
    seccion         text,                -- título de sección si se detectó
    orden           int,                 -- orden del chunk dentro del documento
    embedding       vector(1536),        -- dimensión de text-embedding-3-small
    version_corpus  text not null,
    creado_en       timestamptz default now()
);

-- Índice para búsqueda semántica por similitud coseno
create index if not exists chunks_embedding_idx
    on chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create index if not exists chunks_version_idx on chunks (version_corpus);

-- 4. Factores de emisión estructurados (NO van al vector store: lookup exacto)
create table if not exists factores_emision (
    id              uuid primary key default gen_random_uuid(),
    archivo_origen  text not null,
    hoja            text,                -- nombre de la hoja/pestaña del xlsx
    fila            int,                 -- número de fila de origen (trazabilidad)
    nombre_factor   text not null,       -- ej: "Diésel - combustión fija"
    valor           numeric not null,
    unidad          text not null,       -- ej: "kgCO2e/litro"
    gas             text,                -- CO2 | CH4 | N2O | CO2e | etc.
    fuente          text,                -- ej: "DEFRA 2024", "IPCC 2006"
    anio            int,
    alcance         text not null,       -- 'alcance_1' | 'alcance_2'
    categoria       text not null,       -- combustion_fija | combustion_movil | fugitivos | energia_electrica | energia_termica
    version_corpus  text not null,
    creado_en       timestamptz default now()
);

create index if not exists factores_alcance_categoria_idx
    on factores_emision (alcance, categoria);

create index if not exists factores_version_idx on factores_emision (version_corpus);

-- 5. Función de búsqueda semántica (RPC) para usar desde el backend
create or replace function buscar_chunks_similares(
    query_embedding vector(1536),
    version text,
    top_k int default 5
)
returns table (
    chunk_id uuid,
    documento_id uuid,
    contenido text,
    pagina int,
    seccion text,
    similitud float
)
language sql stable
as $$
    select
        c.id as chunk_id,
        c.documento_id,
        c.contenido,
        c.pagina,
        c.seccion,
        1 - (c.embedding <=> query_embedding) as similitud
    from chunks c
    where c.version_corpus = version
    order by c.embedding <=> query_embedding
    limit top_k;
$$;
