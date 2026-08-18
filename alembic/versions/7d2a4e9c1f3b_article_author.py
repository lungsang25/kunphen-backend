"""article author

Revision ID: 7d2a4e9c1f3b
Revises: 51586e691840
Create Date: 2026-08-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '7d2a4e9c1f3b'
down_revision = '51586e691840'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('author', sa.String(length=200), server_default='', nullable=False))


def downgrade() -> None:
    op.drop_column('articles', 'author')
