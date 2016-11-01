"""Initial db setup

Revision ID: ff7d2ec8988f
Revises: 
Create Date: 2016-10-27 21:56:52.580200

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ff7d2ec8988f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('ready', 'processed', 'failed', name='transactionstatus'), nullable=True),
    sa.Column('collection_format_name', sa.String(length=20), nullable=True),
    sa.Column('collection_format_version', sa.SmallInteger(), nullable=True),
    sa.Column('collection_data', postgresql.JSONB(), nullable=True),
    sa.Column('collection_datetime', sa.DateTime(), nullable=True),
    sa.Column('queue', sa.String(), nullable=True),
    sa.Column('distribution_format_name', sa.String(length=20), nullable=True),
    sa.Column('distribution_format_version', sa.SmallInteger(), nullable=True),
    sa.Column('distribution_data', postgresql.JSONB(), nullable=True),
    sa.Column('distribution_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    op.drop_table('transaction')
    ### end Alembic commands ###
