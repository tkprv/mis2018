"""created new StaffSeminar table to collect seminar record

Revision ID: 92a8e81581a8
Revises: 3b52bfb9803f
Create Date: 2020-09-30 14:14:58.177922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92a8e81581a8'
down_revision = '3b52bfb9803f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('staff_seminar',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('staff_account_id', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('topic_type', sa.String(), nullable=True),
    sa.Column('topic', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('budget_type', sa.String(), nullable=True),
    sa.Column('budget', sa.Float(), nullable=True),
    sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['staff_account_id'], ['staff_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('staff_seminar')
    # ### end Alembic commands ###