"""
Ingesta todos los PDFs del corpus curado:
  corpus_v1/00_fundamentacion/*.pdf
  corpus_v1/01_factores_generales/*.pdf
  corpus_v1/02_alcance1_combustion_fija/*.pdf

Para cada PDF: extrae texto por página -> trocea en chunks -> genera
embeddings -> guarda en Supabase (tablas `documentos` y `chunks`).

Uso:
    python -m app.ingest_pdf
"""
import os
from pathlib import Path
from tqdm import tqdm

from app.config import CORPUS_PATH, CORPUS_VERSION, CATEGORIA_POR_CARPETA
from app.db import get_connection, upsert_documento, insert_chunk, hash_file
from app.chunking import procesar_pdf
from app.embeddings import embed_batch

BATCH_SIZE = 16  # cuántos chunks se embeben juntos por llamada a la API


def encontrar_pdfs() -> list[Path]:
    root = Path(CORPUS_PATH)
    pdfs = []
    for carpeta in CATEGORIA_POR_CARPETA:
        pdfs.extend((root / carpeta).glob("*.pdf"))
    return sorted(pdfs)


def ingestar_pdf(conn, pdf_path: Path):
    categoria = CATEGORIA_POR_CARPETA[pdf_path.parent.name]
    nombre_archivo = pdf_path.name

    documento_id = upsert_documento(
        conn,
        nombre_archivo=nombre_archivo,
        categoria=categoria,
        tipo="pdf",
        version_corpus=CORPUS_VERSION,
        hash_archivo=hash_file(str(pdf_path)),
    )

    chunks = procesar_pdf(str(pdf_path))
    if not chunks:
        print(f"  ! Sin texto extraíble: {nombre_archivo}")
        return

    for i in range(0, len(chunks), BATCH_SIZE):
        lote = chunks[i:i + BATCH_SIZE]
        embeddings = embed_batch([c["contenido"] for c in lote])
        for chunk, embedding in zip(lote, embeddings):
            insert_chunk(
                conn,
                documento_id=documento_id,
                contenido=chunk["contenido"],
                pagina=chunk["pagina"],
                seccion=chunk["seccion"],
                orden=chunk["orden"],
                embedding=embedding,
                version_corpus=CORPUS_VERSION,
            )


def main():
    pdfs = encontrar_pdfs()
    print(f"Encontrados {len(pdfs)} PDFs en {CORPUS_PATH} (versión {CORPUS_VERSION})")

    conn = get_connection()
    try:
        for pdf_path in tqdm(pdfs, desc="Ingestando PDFs"):
            ingestar_pdf(conn, pdf_path)
    finally:
        conn.close()

    print("Listo. Verificá las tablas `documentos` y `chunks` en Supabase.")


if __name__ == "__main__":
    main()
