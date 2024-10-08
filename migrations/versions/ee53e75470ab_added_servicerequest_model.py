"""Added ServiceRequest model

Revision ID: ee53e75470ab
Revises: 1bc7c0c93c65
Create Date: 2024-09-06 08:59:12.256833

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee53e75470ab'
down_revision = '1bc7c0c93c65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_requests',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_requests')
    # ### end Alembic commands ###
