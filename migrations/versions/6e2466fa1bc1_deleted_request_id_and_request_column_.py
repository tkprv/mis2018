"""Deleted request_id and request column in ServicePayment model

Revision ID: 6e2466fa1bc1
Revises: e144f17a57d4
Create Date: 2025-02-03 13:13:20.967345

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6e2466fa1bc1'
down_revision = 'e144f17a57d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_payments', schema=None) as batch_op:
        batch_op.drop_constraint('service_payments_request_id_fkey', type_='foreignkey')
        batch_op.drop_column('request_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('request_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('service_payments_request_id_fkey', 'service_requests', ['request_id'], ['id'])
    # ### end Alembic commands ###
