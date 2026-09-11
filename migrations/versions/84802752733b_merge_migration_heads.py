"""merge migration heads

Revision ID: 84802752733b
Revises: 9ab4cde6fb94, ae90fdf51e63
Create Date: 2026-09-11 21:41:19.467312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84802752733b'
down_revision = ('9ab4cde6fb94', 'ae90fdf51e63')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
