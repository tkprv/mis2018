"""Added ServicePayment model

Revision ID: 5cbce20ec853
Revises: 270cd77429d8
Create Date: 2024-11-15 10:08:58.845020

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5cbce20ec853'
down_revision = '270cd77429d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_payments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('amount_paid', sa.Float(), nullable=False),
    sa.Column('paid_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_payments')
    # ### end Alembic commands ###
