"""Deleted bill_name column in ServiceCustomerAddress model

Revision ID: f5e3815b79c3
Revises: 0893d6bb8487
Create Date: 2024-11-20 09:31:23.058510

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5e3815b79c3'
down_revision = '0893d6bb8487'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_customer_addresses', schema=None) as batch_op:
        batch_op.drop_column('bill_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_customer_addresses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bill_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###