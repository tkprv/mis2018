"""added the association table for KPIs and datasets

Revision ID: aefb45638b1e
Revises: 16f609d0a81c
Create Date: 2022-02-26 23:37:21.288138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aefb45638b1e'
down_revision = '16f609d0a81c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dataset_kpi_assoc',
    sa.Column('dataset_id', sa.Integer(), nullable=False),
    sa.Column('kpi_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['dataset_id'], ['db_datasets.id'], ),
    sa.ForeignKeyConstraint(['kpi_id'], ['kpis.id'], ),
    sa.PrimaryKeyConstraint('dataset_id', 'kpi_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dataset_kpi_assoc')
    # ### end Alembic commands ###
