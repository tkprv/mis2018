"""Added ServiceSampleAppointment model

Revision ID: 60ee1e2239b6
Revises: 4bb6ed7d46b5
Create Date: 2024-11-15 09:38:34.727069

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '60ee1e2239b6'
down_revision = '4bb6ed7d46b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_sample_appointments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('appointment_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('service_sample_appointments')
    # ### end Alembic commands ###
