"""created pa_approved_score_sheets table

Revision ID: e7b3622541f5
Revises: 3cd44e6e559f
Create Date: 2023-06-19 22:44:06.456586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7b3622541f5'
down_revision = '3cd44e6e559f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pa_approved_score_sheets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('score_sheet_id', sa.Integer(), nullable=True),
    sa.Column('committee_id', sa.Integer(), nullable=True),
    sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['committee_id'], ['pa_committees.id'], ),
    sa.ForeignKeyConstraint(['score_sheet_id'], ['pa_score_sheets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pa_approved_score_sheets')
    # ### end Alembic commands ###
