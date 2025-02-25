"""Added ServiceAdmin model

Revision ID: 26f076a53c27
Revises: 15a5a4aaf710
Create Date: 2024-12-27 16:04:17.982599

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '26f076a53c27'
down_revision = '15a5a4aaf710'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_admins',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('lab_id', sa.Integer(), nullable=True),
    sa.Column('sub_lab_id', sa.Integer(), nullable=True),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['staff_account.id'], ),
    sa.ForeignKeyConstraint(['lab_id'], ['service_labs.id'], ),
    sa.ForeignKeyConstraint(['sub_lab_id'], ['service_sub_labs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_admins')
    # ### end Alembic commands ###
