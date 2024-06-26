"""added some more fields to the requests

Revision ID: 463c6236fa58
Revises: 02cc87f01969
Create Date: 2022-05-22 22:59:36.360116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '463c6236fa58'
down_revision = '02cc87f01969'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pdpa_requests', sa.Column('detail', sa.Text(), nullable=True))
    op.add_column('pdpa_requests', sa.Column('received_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('pdpa_requests', sa.Column('received_by', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'pdpa_requests', 'staff_account', ['received_by'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'pdpa_requests', type_='foreignkey')
    op.drop_column('pdpa_requests', 'received_by')
    op.drop_column('pdpa_requests', 'received_at')
    op.drop_column('pdpa_requests', 'detail')
    # ### end Alembic commands ###
