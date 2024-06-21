"""Delete is_notification column in ComplaintAdmin model

Revision ID: a459e6222d7b
Revises: adceba1dbd4f
Create Date: 2024-06-04 11:36:24.169537

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a459e6222d7b'
down_revision = 'adceba1dbd4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('complaint_admins', schema=None) as batch_op:
        batch_op.drop_column('is_notification')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('complaint_admins', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_notification', sa.BOOLEAN(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###