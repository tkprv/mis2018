"""Added sender_id, sender, receipient_id and receipient column in ServiceSampleAppointment model

Revision ID: 6eae28f414a8
Revises: ca832f94cf64
Create Date: 2025-01-14 11:15:29.341239

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6eae28f414a8'
down_revision = 'ca832f94cf64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_sample_appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sender_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recipient_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'staff_account', ['recipient_id'], ['id'])
        batch_op.create_foreign_key(None, 'service_customer_accounts', ['sender_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service_sample_appointments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('recipient_id')
        batch_op.drop_column('sender_id')
    # ### end Alembic commands ###
