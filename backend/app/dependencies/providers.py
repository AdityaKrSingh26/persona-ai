from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.repositories.meta_repository import MetaRepository


def get_meta_repo(db: AsyncSession = Depends(get_db)) -> MetaRepository:
    return MetaRepository(db)


# Phase 3 providers — filled once integrations and repos exist
# Imported here to keep the import surface clean for routers

def get_source_repo(db: AsyncSession = Depends(get_db)):
    from app.repositories.source_repository import SourceRepository
    return SourceRepository(db)


def get_chunk_repo(db: AsyncSession = Depends(get_db)):
    from app.repositories.chunk_repository import ChunkRepository
    return ChunkRepository(db)


def get_session_repo(db: AsyncSession = Depends(get_db)):
    from app.repositories.session_repository import SessionRepository
    return SessionRepository(db)


def get_embeddings_client():
    from app.integrations.embeddings_api import EmbeddingsClient
    from app.config import settings
    return EmbeddingsClient(settings.github_models_api_key, settings.github_models_endpoint)


def get_github_client():
    from app.integrations.github import GitHubClient
    from app.config import settings
    return GitHubClient(settings.github_token, settings.github_username)
