"""
Configuración centralizada del pipeline de ingesta.
Carga las variables de entorno desde .env
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
CORPUS_VERSION = os.environ["CORPUS_VERSION"]
CORPUS_PATH = os.environ.get("CORPUS_PATH", "./corpus_v1")

# Tamaño objetivo de cada chunk de texto (en tokens aproximados) y solapamiento
CHUNK_SIZE_TOKENS = 400
CHUNK_OVERLAP_TOKENS = 60

# Mapeo carpeta del corpus -> categoría almacenada en la tabla `documentos`
CATEGORIA_POR_CARPETA = {
    "00_fundamentacion": "fundamentacion",
    "01_factores_generales": "factores_generales",
    "02_alcance1_combustion_fija": "alcance1_combustion_fija",
}
