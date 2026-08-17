"""
Generación de embeddings vía OpenAI para los chunks de texto.
"""
from openai import OpenAI
from app.config import OPENAI_API_KEY, EMBEDDING_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)


def embed_texto(texto: str) -> list[float]:
    response = _client.embeddings.create(model=EMBEDDING_MODEL, input=texto)
    return response.data[0].embedding


def embed_batch(textos: list[str]) -> list[list[float]]:
    """OpenAI acepta batches de hasta ~2048 inputs por llamada; acá lo dejamos simple."""
    response = _client.embeddings.create(model=EMBEDDING_MODEL, input=textos)
    return [item.embedding for item in response.data]
