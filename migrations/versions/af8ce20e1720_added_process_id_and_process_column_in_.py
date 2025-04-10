"""added process_id and process column in SoftwareRequestDetail model

Revision ID: af8ce20e1720
Revises: 3bfd9e8433f9
Create Date: 2025-03-21 09:50:35.053860

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'af8ce20e1720'
down_revision = '3bfd9e8433f9'
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
