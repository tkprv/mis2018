"""created item_kpi_item_assoc_table table

Revision ID: 4aa6db573404
Revises: 64f3c94e6890
Create Date: 2023-06-17 09:19:22.393607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4aa6db573404'
down_revision = '64f3c94e6890'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item_kpi_item_assoc_assoc',
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('kpi_item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['pa_items.id'], ),
    sa.ForeignKeyConstraint(['kpi_item_id'], ['pa_kpi_items.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('item_kpi_item_assoc_assoc')
    # ### end Alembic commands ###