"""changed foreign key null constraints

Revision ID: d3ed12366589
Revises: c745a0c48219
Create Date: 2024-08-08 18:53:06.964248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3ed12366589'
down_revision = 'c745a0c48219'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mentors_checklist', schema=None) as batch_op:
        batch_op.alter_column('cme_unique_id',
               existing_type=sa.BIGINT(),
               nullable=True)
        batch_op.alter_column('drill_unique_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mentors_checklist', schema=None) as batch_op:
        batch_op.alter_column('drill_unique_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('cme_unique_id',
               existing_type=sa.BIGINT(),
               nullable=False)

    # ### end Alembic commands ###
