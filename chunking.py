"""
Extrae texto de un PDF página por página y lo trocea en chunks,
conservando el número de página como metadato para citación exacta.
"""
import re
import pdfplumber
import tiktoken
from app.config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS

_encoder = tiktoken.get_encoding("cl100k_base")

# Heurística simple para detectar títulos de sección (líneas cortas, en mayúsculas
# o que empiezan con un patrón "1.", "1.2", "Capítulo", etc.)
_SECTION_PATTERN = re.compile(
    r"^\s*((\d+(\.\d+)*\s+)|(cap[ií]tulo\s+\d+)|([A-ZÁÉÍÓÚÑ\s]{6,}))",
    re.IGNORECASE,
)


def _detectar_seccion(linea: str) -> bool:
    linea = linea.strip()
    if not linea or len(linea) > 90:
        return False
    return bool(_SECTION_PATTERN.match(linea))


def extraer_paginas(pdf_path: str) -> list[dict]:
    """Devuelve [{pagina, texto}] con el texto crudo de cada página."""
    paginas = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            texto = page.extract_text() or ""
            paginas.append({"pagina": i, "texto": texto})
    return paginas


def chunkear_texto(texto: str, max_tokens: int = CHUNK_SIZE_TOKENS,
                    overlap_tokens: int = CHUNK_OVERLAP_TOKENS) -> list[str]:
    """Trocea un texto largo en fragmentos de ~max_tokens con solapamiento."""
    tokens = _encoder.encode(texto)
    if not tokens:
        return []

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(_encoder.decode(chunk_tokens))
        if end == len(tokens):
            break
        start = end - overlap_tokens
    return chunks


def procesar_pdf(pdf_path: str) -> list[dict]:
    """
    Devuelve una lista de chunks listos para insertar:
    [{contenido, pagina, seccion, orden}]
    """
    paginas = extraer_paginas(pdf_path)
    resultado = []
    orden = 0
    seccion_actual = None

    for pagina in paginas:
        # Actualizar sección detectada en esta página (si hay una línea que matchea)
        for linea in pagina["texto"].splitlines():
            if _detectar_seccion(linea):
                seccion_actual = linea.strip()
                break

        for chunk_texto in chunkear_texto(pagina["texto"]):
            if not chunk_texto.strip():
                continue
            resultado.append({
                "contenido": chunk_texto.strip(),
                "pagina": pagina["pagina"],
                "seccion": seccion_actual,
                "orden": orden,
            })
            orden += 1

    return resultado
