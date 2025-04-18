"""Added process_id and process column in SoftwareRequestDetail model

Revision ID: 5a4735a6bbb5
Revises: 5429fb2494fe
Create Date: 2025-03-21 14:11:31.864285

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5a4735a6bbb5'
down_revision = '5429fb2494fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('software_request_details', schema=None) as batch_op:
        batch_op.add_column(sa.Column('process_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'db_processes', ['process_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('software_request_details', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('process_id')
    # ### end Alembic commands ###
