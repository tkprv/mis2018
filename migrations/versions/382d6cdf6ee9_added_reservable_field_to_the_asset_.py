"""added reservable field to the asset_items

Revision ID: 382d6cdf6ee9
Revises: 04886025910a
Create Date: 2019-01-04 08:09:04.392408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '382d6cdf6ee9'
down_revision = '04886025910a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asset_items', sa.Column('en_desc', sa.String(length=255), nullable=True,
                                           server_default=''))
    op.add_column('asset_items', sa.Column('reservable', sa.Boolean(), nullable=True))
    op.add_column('asset_items', sa.Column('th_desc', sa.String(length=255), nullable=False,
                                           server_default='Unknown'))
    op.drop_column('asset_items', 'desc')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('asset_items', sa.Column('desc', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_column('asset_items', 'th_desc')
    op.drop_column('asset_items', 'reservable')
    op.drop_column('asset_items', 'en_desc')
    # ### end Alembic commands ###