"""Updated name, procurement no column can not null to null

Revision ID: 9b3eb7509a20
Revises: ecc4b3eac2f5
Create Date: 2022-11-14 14:01:04.937000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b3eb7509a20'
down_revision = 'ecc4b3eac2f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('procurement_details', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('procurement_details', 'procurement_no',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('procurement_details', 'procurement_no',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('procurement_details', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    # ### end Alembic commands ###
