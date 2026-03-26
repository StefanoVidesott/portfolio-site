"""add project enhancements, open_to_work and cv_documents

Revision ID: b3e7f1a9c2d5
Revises: ffabae6db375
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b3e7f1a9c2d5'
down_revision: Union[str, Sequence[str], None] = 'ffabae6db375'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- projects: new columns ---
    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(sa.Column("is_case_study", sa.Boolean(), nullable=True, server_default=sa.false()))
        batch_op.add_column(sa.Column("internal_url", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("tags", sa.String(), nullable=True))

    # Backfill known projects with internal URLs, case-study flags and tech tags
    op.execute(
        "UPDATE projects SET internal_url = '/project/wannawork', is_case_study = 1, "
        "tags = 'Vue.js 3, Node.js, Express, MongoDB, Docker, JWT' WHERE slug = 'wannawork'"
    )
    op.execute(
        "UPDATE projects SET internal_url = '/project/portfolio', is_case_study = 1, "
        "tags = 'Python, FastAPI, SQLAlchemy, Docker, Vanilla JS, GitHub Actions' "
        "WHERE slug = 'portfolio-headless-cms'"
    )
    op.execute(
        "UPDATE projects SET tags = 'C++, OpenGL, Game Dev' WHERE slug = 'air-force-1943'"
    )
    op.execute(
        "UPDATE projects SET tags = 'Python, Bash, Linux' WHERE slug = 'unitn-p2-configuration'"
    )

    # --- open_to_work table ---
    op.create_table(
        "open_to_work",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("badge_it", sa.String(), nullable=True),
        sa.Column("title_it", sa.String(), nullable=True),
        sa.Column("message_it", sa.String(), nullable=True),
        sa.Column("badge_en", sa.String(), nullable=True),
        sa.Column("title_en", sa.String(), nullable=True),
        sa.Column("message_en", sa.String(), nullable=True),
    )
    # Insert a disabled default record so the admin can enable it at any time
    op.execute(
        "INSERT INTO open_to_work (is_enabled, badge_it, title_it, message_it, badge_en, title_en, message_en) "
        "VALUES (0, "
        "'Disponibile', 'Cerco nuove opportunità', 'Sono aperto a posizioni full-time, stage o freelance. Contattami!', "
        "'Available', 'Open to opportunities', 'I am open to full-time, internship, or freelance positions. Get in touch!')"
    )

    # --- cv_documents table ---
    op.create_table(
        "cv_documents",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("lang", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("file_url", sa.String(), nullable=False),
    )
    # Seed with the existing static CV files so the site works immediately
    op.execute(
        "INSERT INTO cv_documents (lang, label, file_url) VALUES "
        "('it', 'CV Italiano', '/static/docs/it/CV_Stefano_Videsott.pdf'), "
        "('en', 'CV English', '/static/docs/en/CV_Stefano_Videsott.pdf')"
    )


def downgrade() -> None:
    op.drop_table("cv_documents")
    op.drop_table("open_to_work")

    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_column("tags")
        batch_op.drop_column("internal_url")
        batch_op.drop_column("is_case_study")
