"""Added result_id and result column in ServiceRequest model

Revision ID: 0d57d2273a0c
Revises: 2fb721bb05ca
Create Date: 2024-11-21 14:43:11.659759

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0d57d2273a0c'
down_revision = '2fb721bb05ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('result_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'service_results', ['result_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_requests', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('result_id')
    # ### end Alembic commands ###