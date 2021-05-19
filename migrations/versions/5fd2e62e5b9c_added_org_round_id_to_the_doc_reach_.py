"""added org round Id to the doc reach model

Revision ID: 5fd2e62e5b9c
Revises: 742025ba7ee8
Create Date: 2021-05-19 23:05:01.552275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fd2e62e5b9c'
down_revision = '742025ba7ee8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doc_document_reaches', sa.Column('reacher_id', sa.Integer(), nullable=True))
    op.add_column('doc_document_reaches', sa.Column('round_org_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'doc_document_reaches_reached_by_fkey', 'doc_document_reaches', type_='foreignkey')
    op.create_foreign_key(None, 'doc_document_reaches', 'doc_round_orgs', ['round_org_id'], ['id'])
    op.create_foreign_key(None, 'doc_document_reaches', 'staff_account', ['reacher_id'], ['id'])
    op.drop_column('doc_document_reaches', 'reached_by')
    op.add_column('doc_round_org_reaches', sa.Column('reacher_id', sa.Integer(), nullable=True))
    op.drop_constraint(u'doc_round_org_reaches_reached_by_fkey', 'doc_round_org_reaches', type_='foreignkey')
    op.create_foreign_key(None, 'doc_round_org_reaches', 'staff_account', ['reacher_id'], ['id'])
    op.drop_column('doc_round_org_reaches', 'reached_by')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doc_round_org_reaches', sa.Column('reached_by', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'doc_round_org_reaches', type_='foreignkey')
    op.create_foreign_key(u'doc_round_org_reaches_reached_by_fkey', 'doc_round_org_reaches', 'staff_account', ['reached_by'], ['id'])
    op.drop_column('doc_round_org_reaches', 'reacher_id')
    op.add_column('doc_document_reaches', sa.Column('reached_by', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'doc_document_reaches', type_='foreignkey')
    op.drop_constraint(None, 'doc_document_reaches', type_='foreignkey')
    op.create_foreign_key(u'doc_document_reaches_reached_by_fkey', 'doc_document_reaches', 'staff_account', ['reached_by'], ['id'])
    op.drop_column('doc_document_reaches', 'round_org_id')
    op.drop_column('doc_document_reaches', 'reacher_id')
    # ### end Alembic commands ###