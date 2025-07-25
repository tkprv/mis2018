"""Added short_address column in ServiceSubLab model

Revision ID: 5ee83ed82ce8
Revises: c4b6170397c0
Create Date: 2025-07-08 21:40:45.626344

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5ee83ed82ce8'
down_revision = 'c4b6170397c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_sub_labs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('short_address', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_sub_labs', schema=None) as batch_op:
        batch_op.drop_column('short_address')
    # ### end Alembic commands ###
