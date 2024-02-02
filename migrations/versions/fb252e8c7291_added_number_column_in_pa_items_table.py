"""added number column in pa_items table

Revision ID: fb252e8c7291
Revises: 48a6124e0fa6
Create Date: 2023-08-18 15:27:50.194278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb252e8c7291'
down_revision = '48a6124e0fa6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pa_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('number', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pa_items', schema=None) as batch_op:
        batch_op.drop_column('number')

    # ### end Alembic commands ###