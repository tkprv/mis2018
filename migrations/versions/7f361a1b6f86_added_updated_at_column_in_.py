"""Added updated_at column in ComplaintRepairApproval model

Revision ID: 7f361a1b6f86
Revises: 87a4043c2b45
Create Date: 2025-07-02 13:38:18.614090

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7f361a1b6f86'
down_revision = '87a4043c2b45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('complaint_repair_approvals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('complaint_repair_approvals', schema=None) as batch_op:
        batch_op.drop_column('updated_at')
    # ### end Alembic commands ###
