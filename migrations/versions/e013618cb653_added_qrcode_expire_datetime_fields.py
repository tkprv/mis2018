"""added qrcode expire datetime fields

Revision ID: e013618cb653
Revises: 1f41d4e2b6da
Create Date: 2022-08-02 14:40:44.258603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e013618cb653'
down_revision = '1f41d4e2b6da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('staff_work_logins', sa.Column('qrcode_in_exp_datetime', sa.DateTime(timezone=True), nullable=True))
    op.add_column('staff_work_logins', sa.Column('qrcode_out_exp_datetime', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('staff_work_logins', 'qrcode_out_exp_datetime')
    op.drop_column('staff_work_logins', 'qrcode_in_exp_datetime')
    # ### end Alembic commands ###
