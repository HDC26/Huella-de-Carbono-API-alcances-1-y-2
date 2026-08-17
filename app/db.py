"""
Helpers de conexión y escritura a Postgres/Supabase.
"""
import hashlib
import psycopg2
import psycopg2.extras
from app.config import DATABASE_URL

psycopg2.extras.register_uuid()


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def hash_file(path: str) -> str:
    """Hash del archivo para detectar cambios entre versiones del corpus."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


def upsert_documento(conn, nombre_archivo: str, categoria: str, tipo: str,
                      version_corpus: str, hash_archivo: str) -> str:
    """
    Inserta el registro del documento y devuelve su id.
    Si ya existe el mismo archivo+versión, lo reutiliza (idempotente).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            select id from documentos
            where nombre_archivo = %s and version_corpus = %s
            """,
            (nombre_archivo, version_corpus),
        )
        row = cur.fetchone()
        if row:
            return row[0]

        cur.execute(
            """
            insert into documentos (nombre_archivo, categoria, tipo, version_corpus, hash_archivo)
            values (%s, %s, %s, %s, %s)
            returning id
            """,
            (nombre_archivo, categoria, tipo, version_corpus, hash_archivo),
        )
        doc_id = cur.fetchone()[0]
        conn.commit()
        return doc_id


def insert_chunk(conn, documento_id: str, contenido: str, pagina: int,
                  seccion: str, orden: int, embedding: list, version_corpus: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into chunks
                (documento_id, contenido, pagina, seccion, orden, embedding, version_corpus)
            values (%s, %s, %s, %s, %s, %s, %s)
            """,
            (documento_id, contenido, pagina, seccion, orden, embedding, version_corpus),
        )
    conn.commit()


def insert_factor(conn, archivo_origen: str, hoja: str, fila: int, nombre_factor: str,
                   valor: float, unidad: str, gas: str, fuente: str, anio: int,
                   alcance: str, categoria: str, version_corpus: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into factores_emision
                (archivo_origen, hoja, fila, nombre_factor, valor, unidad, gas,
                 fuente, anio, alcance, categoria, version_corpus)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (archivo_origen, hoja, fila, nombre_factor, valor, unidad, gas,
             fuente, anio, alcance, categoria, version_corpus),
        )
    conn.commit()
