"""Added ComplaintSubTopic Model

Revision ID: d502c0b33b9e
Revises: 4ef22b28ed3c
Create Date: 2024-02-12 13:48:10.013454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd502c0b33b9e'
down_revision = '4ef22b28ed3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('complaint_sub_topics',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('subtopic', sa.String(), nullable=True),
    sa.Column('topic_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['topic_id'], ['complaint_topics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('complaint_sub_topics')
    # ### end Alembic commands ###