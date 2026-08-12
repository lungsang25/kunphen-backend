"""hero slides

Revision ID: c3f71a0d5b42
Revises: 8c41d2a7e5b6
Create Date: 2026-08-12 11:20:04.512338

"""
from alembic import op
import sqlalchemy as sa

revision = 'c3f71a0d5b42'
down_revision = '8c41d2a7e5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('hero_slides',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=1000), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('subtitle', sa.String(length=500), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('hero_slides')
