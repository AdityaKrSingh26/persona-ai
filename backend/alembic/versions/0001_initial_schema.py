"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-06-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector extension — required before any VECTOR column
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # sources
    op.create_table(
        "sources",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "type",
            sa.Text(),
            sa.CheckConstraint("type IN ('resume', 'url')", name="sources_type_check"),
            nullable=False,
        ),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Text(),
            sa.CheckConstraint("status IN ('ready', 'failed')", name="sources_status_check"),
            nullable=False,
            server_default="ready",
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("indexed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # One resume max — enforced at DB level
    op.create_index(
        "one_resume",
        "sources",
        ["type"],
        unique=True,
        postgresql_where=sa.text("type = 'resume'"),
    )
    # No duplicate URLs
    op.create_index(
        "unique_url",
        "sources",
        ["url"],
        unique=True,
        postgresql_where=sa.text("url IS NOT NULL"),
    )

    # updated_at trigger — app-level updates are forgettable; the trigger is not
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER sources_updated_at
            BEFORE UPDATE ON sources
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    # chunks
    op.create_table(
        "chunks",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "source_id",
            sa.UUID(),
            sa.ForeignKey("sources.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=True),  # placeholder; real type below
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    # Replace the placeholder column type with the real pgvector type
    op.execute("ALTER TABLE chunks ALTER COLUMN embedding TYPE vector(1536) USING NULL::vector(1536)")

    op.create_index("chunks_source_idx", "chunks", ["source_id"])

    # HNSW vector index — not IVFFlat: HNSW needs no training step, handles small datasets well,
    # gives better recall, and stays correct as rows are inserted
    op.execute(
        "CREATE INDEX chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops)"
    )

    # sessions — written by Vapi call-start / call-end webhooks
    op.create_table(
        "sessions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("vapi_call_id", sa.Text(), nullable=False, unique=True),
        sa.Column(
            "started_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ended_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
    )

    # app_meta — single row, holds token_version for JWT revocation
    op.create_table(
        "app_meta",
        sa.Column(
            "id",
            sa.Integer(),
            sa.CheckConstraint("id = 1", name="app_meta_single_row"),
            primary_key=True,
        ),
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="1"),
    )
    # Seed the single row
    op.execute("INSERT INTO app_meta (id, token_version) VALUES (1, 1)")


def downgrade() -> None:
    op.drop_table("app_meta")
    op.drop_table("sessions")
    op.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS chunks_source_idx")
    op.drop_table("chunks")
    op.execute("DROP TRIGGER IF EXISTS sources_updated_at ON sources")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at")
    op.drop_index("unique_url", table_name="sources")
    op.drop_index("one_resume", table_name="sources")
    op.drop_table("sources")
    op.execute("DROP EXTENSION IF EXISTS vector")
