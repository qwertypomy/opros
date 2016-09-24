"""empty message

Revision ID: 460d5e55638f
Revises: None
Create Date: 2016-09-24 14:59:35.521293

"""

# revision identifiers, used by Alembic.
revision = '460d5e55638f'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=16), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('user_name', sa.String(length=32), nullable=False),
    sa.Column('api_key', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_api_key'), 'user', ['api_key'], unique=True)
    op.create_table('poll',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=256), nullable=False),
    sa.Column('poll_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['poll_id'], ['poll.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=128), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answer')
    op.drop_table('question')
    op.drop_table('poll')
    op.drop_index(op.f('ix_user_api_key'), table_name='user')
    op.drop_table('user')
    ### end Alembic commands ###