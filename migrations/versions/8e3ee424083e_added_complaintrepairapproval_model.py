"""Added ComplaintRepairApproval model

Revision ID: 8e3ee424083e
Revises: dec525d8082e
Create Date: 2025-07-04 15:46:31.904761

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8e3ee424083e'
down_revision = 'dec525d8082e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('complaint_repair_approvals',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('mhesi_no', sa.String(), nullable=True),
    sa.Column('mhesi_no_date', sa.Date(), nullable=True),
    sa.Column('procurement_no', sa.String(), nullable=True),
    sa.Column('repair_type', sa.String(), nullable=True),
    sa.Column('principle_approval_type', sa.String(), nullable=True),
    sa.Column('requester_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('position', sa.String(), nullable=True),
    sa.Column('organization', sa.String(), nullable=True),
    sa.Column('item', sa.String(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('detail', sa.Text(), nullable=True),
    sa.Column('purpose', sa.Text(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('budget_source', sa.String(), nullable=True),
    sa.Column('book_number', sa.String(), nullable=True),
    sa.Column('receipt_number', sa.String(), nullable=True),
    sa.Column('receipt_date', sa.Date(), nullable=True),
    sa.Column('purchase_type', sa.String(), nullable=True),
    sa.Column('budget_year', sa.Integer(), nullable=True),
    sa.Column('cost_center_id', sa.String(length=12), nullable=True),
    sa.Column('io_code_id', sa.String(length=16), nullable=True),
    sa.Column('product_code_id', sa.String(length=12), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('borrower_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('record_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['borrower_id'], ['staff_account.id'], ),
    sa.ForeignKeyConstraint(['cost_center_id'], ['cost_centers.id'], ),
    sa.ForeignKeyConstraint(['creator_id'], ['staff_account.id'], ),
    sa.ForeignKeyConstraint(['io_code_id'], ['iocodes.id'], ),
    sa.ForeignKeyConstraint(['product_code_id'], ['product_codes.id'], ),
    sa.ForeignKeyConstraint(['record_id'], ['complaint_records.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['staff_account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('complaint_repair_approvals')
    # ### end Alembic commands ###
