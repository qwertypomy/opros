"""empty message

Revision ID: fbcd1a6ee8d1
Revises: 460d5e55638f
Create Date: 2016-09-24 15:01:31.721814

"""

# revision identifiers, used by Alembic.
revision = 'fbcd1a6ee8d1'
down_revision = '460d5e55638f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('answer_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'answer', ['answer_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'answer_id')
    ### end Alembic commands ###
