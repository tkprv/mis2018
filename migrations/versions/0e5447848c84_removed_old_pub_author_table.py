"""removed old pub author table

Revision ID: 0e5447848c84
Revises: 3a1e1f15a3a6
Create Date: 2020-11-06 10:49:11.002333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e5447848c84'
down_revision = '3a1e1f15a3a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pub_author_assoc',
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('pub_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['staff_personal_info.id'], ),
    sa.ForeignKeyConstraint(['pub_id'], ['research_pub.id'], )
    )
    op.drop_table('pub_author_table')
    op.add_column('research_pub', sa.Column('doi', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('research_pub', 'doi')
    op.create_table('pub_author_table',
    sa.Column('author_email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('pub_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['author_email'], [u'staff_account.email'], name=u'pub_author_table_author_email_fkey'),
    sa.ForeignKeyConstraint(['pub_id'], [u'research_pub.id'], name=u'pub_author_table_pub_id_fkey'),
    sa.ForeignKeyConstraint(['pub_id'], [u'research_pub.id'], name=u'pub_author_table_pub_id_fkey1'),
    sa.PrimaryKeyConstraint('author_email', 'pub_id', name=u'pub_author_table_pkey')
    )
    op.drop_table('pub_author_assoc')
    # ### end Alembic commands ###