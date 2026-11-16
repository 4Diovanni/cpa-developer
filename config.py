"""Configuração do Flask lida do .env (nada sensível fica no código)."""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _url_banco() -> str:
    """Monta a URL do PostgreSQL do Supabase para o SQLAlchemy.

    Usa DATABASE_URL se existir (ex.: string do pooler do Supabase, necessária
    em hospedagens sem IPv6 como a Vercel). Caso contrário, monta a conexão
    direta a partir das variáveis SUPABASE_DB_*.
    """
    url = os.getenv("DATABASE_URL")
    if url:
        for prefixo in ("postgres://", "postgresql://"):
            if url.startswith(prefixo):
                return "postgresql+psycopg://" + url[len(prefixo) :]
        return url

    usuario = os.environ["SUPABASE_DB_USER"]
    senha = quote_plus(os.environ["SUPABASE_DB_PASSWORD"])
    host = os.environ["SUPABASE_DB_HOST"]
    porta = os.getenv("SUPABASE_DB_PORT", "5432")
    banco = os.getenv("SUPABASE_DB_NAME", "postgres")
    return f"postgresql+psycopg://{usuario}:{senha}@{host}:{porta}/{banco}?sslmode=require"


class Config:
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

    SQLALCHEMY_DATABASE_URI = _url_banco()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        # O pooler do Supabase em modo transação não aceita prepared statements.
        "connect_args": {"prepare_threshold": None},
    }

    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_PUBLISHABLE_KEY = os.environ["SUPABASE_PUBLISHABLE_KEY"]
    SUPABASE_SECRET_KEY = os.environ["SUPABASE_SECRET_KEY"]
