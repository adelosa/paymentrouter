"""add systemcontrol

Revision ID: 510a2e8a0c4e
Revises: ff7d2ec8988f
Create Date: 2016-11-03 18:39:20.290081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '510a2e8a0c4e'
down_revision = 'ff7d2ec8988f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'syscontrol',
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('system_id')
    )


def downgrade():
    op.drop_table('syscontrol')
