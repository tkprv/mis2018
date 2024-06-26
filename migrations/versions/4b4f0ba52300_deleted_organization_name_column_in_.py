"""Deleted organization_name column in ServiceCustomerInfo model

Revision ID: 4b4f0ba52300
Revises: 350c0d9ef093
Create Date: 2024-04-30 13:40:32.246091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b4f0ba52300'
down_revision = '350c0d9ef093'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_customer_infos', schema=None) as batch_op:
        batch_op.drop_column('organization_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_customer_infos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('organization_name', sa.VARCHAR(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
