"""Deleted customer_id and customer column in ServiceCustomerAddress model

Revision ID: 4a903981cc42
Revises: 757fe69ca056
Create Date: 2024-12-04 11:19:55.191713

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4a903981cc42'
down_revision = '757fe69ca056'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_customer_addresses', schema=None) as batch_op:
        batch_op.drop_constraint('service_customer_addresses_customer_id_fkey', type_='foreignkey')
        batch_op.drop_column('customer_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_customer_addresses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('service_customer_addresses_customer_id_fkey', 'service_customer_accounts', ['customer_id'], ['id'])
    # ### end Alembic commands ###