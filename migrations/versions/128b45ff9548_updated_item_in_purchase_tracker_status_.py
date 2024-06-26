"""Updated item in Purchase Tracker Status and Renamed Thai status_date

Revision ID: 128b45ff9548
Revises: 40d64090ba91
Create Date: 2021-12-01 14:47:27.619000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '128b45ff9548'
down_revision = '40d64090ba91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tracker_statuses', sa.Column('item_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tracker_statuses', 'tracker_accounts', ['item_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tracker_statuses', type_='foreignkey')
    op.drop_column('tracker_statuses', 'item_id')
    # ### end Alembic commands ###
