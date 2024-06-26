"""Added assignee_id and assignee in ComplaintRecord model

Revision ID: 5e64188b99dd
Revises: a60c72740e4e
Create Date: 2024-06-21 15:40:23.971172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e64188b99dd'
down_revision = 'a60c72740e4e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('complaint_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assignee_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'complaint_admins', ['assignee_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('complaint_records', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('assignee_id')

    # ### end Alembic commands ###
