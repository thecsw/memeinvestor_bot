"""move to sqlalchemy

Revision ID: bfd0d78cd176
Revises: 
Create Date: 2018-05-31 20:04:29.822914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bfd0d78cd176'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("Investors", "active")


def downgrade():
    pass
