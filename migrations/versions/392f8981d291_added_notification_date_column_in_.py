"""Added notification_date column in meeting_poll_participant_assoc table

Revision ID: 392f8981d291
Revises: bccbad6e60e2
Create Date: 2025-04-21 14:49:08.309792

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '392f8981d291'
down_revision = 'bccbad6e60e2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meeting_poll_participant_assoc', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notification_date', sa.DateTime(timezone=True), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meeting_poll_participant_assoc', schema=None) as batch_op:
        batch_op.drop_column('notification_date')
    # ### end Alembic commands ###
