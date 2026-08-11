"""gallery albums

Revision ID: 8c41d2a7e5b6
Revises: 1b038073f8d9
Create Date: 2026-08-12 10:42:18.113905

"""
from alembic import op
import sqlalchemy as sa

revision = '8c41d2a7e5b6'
down_revision = '1b038073f8d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('gallery_albums',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('sort_order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('gallery_images', sa.Column('album_id', sa.Integer(), nullable=True))

    # Every existing image becomes a one-image album. The image's caption is promoted
    # to the album title (albums are what the public grid labels now), so the per-image
    # caption is cleared rather than duplicated. A temporary column carries the source
    # image id so the backfill mapping is deterministic.
    op.execute("ALTER TABLE gallery_albums ADD COLUMN _legacy_image_id INTEGER")
    op.execute(
        """
        INSERT INTO gallery_albums (title, sort_order, created_at, updated_at, _legacy_image_id)
        SELECT caption, sort_order, created_at, now(), id FROM gallery_images
        """
    )
    op.execute(
        """
        UPDATE gallery_images gi SET album_id = ga.id
        FROM gallery_albums ga WHERE ga._legacy_image_id = gi.id
        """
    )
    op.execute("ALTER TABLE gallery_albums DROP COLUMN _legacy_image_id")
    op.execute("UPDATE gallery_images SET caption = '', sort_order = 0")

    op.alter_column('gallery_images', 'album_id', nullable=False)
    op.create_foreign_key(
        'fk_gallery_images_album_id_gallery_albums',
        'gallery_images', 'gallery_albums',
        ['album_id'], ['id'],
        ondelete='CASCADE',
    )
    op.create_index(op.f('ix_gallery_images_album_id'), 'gallery_images', ['album_id'])


def downgrade() -> None:
    # Collapse each album back onto its images: the album title returns to the caption
    # and the album's position returns to the image's sort_order. Albums holding more
    # than one image will leave several rows sharing a caption and sort_order.
    op.execute(
        """
        UPDATE gallery_images gi
        SET caption = ga.title, sort_order = ga.sort_order
        FROM gallery_albums ga WHERE ga.id = gi.album_id
        """
    )
    op.drop_index(op.f('ix_gallery_images_album_id'), table_name='gallery_images')
    op.drop_constraint(
        'fk_gallery_images_album_id_gallery_albums', 'gallery_images', type_='foreignkey'
    )
    op.drop_column('gallery_images', 'album_id')
    op.drop_table('gallery_albums')
