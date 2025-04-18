"""Added request_id and request column in ServicePayment model

Revision ID: 1aafbb004e1d
Revises: afafba74e05c
Create Date: 2025-01-30 15:26:19.077895

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1aafbb004e1d'
down_revision = 'afafba74e05c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_payments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('request_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'service_requests', ['request_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_payments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('request_id')
    # ### end Alembic commands ###
