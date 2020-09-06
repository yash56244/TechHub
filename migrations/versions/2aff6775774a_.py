"""empty message

Revision ID: 2aff6775774a
Revises: 7cb7f19ede49
Create Date: 2020-09-06 13:03:53.807535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2aff6775774a'
down_revision = '7cb7f19ede49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cart', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'cart', 'user', ['user_id'], ['id'])
    op.add_column('product', sa.Column('card_id', sa.Integer(), nullable=False))
    op.add_column('product', sa.Column('quantity_in_cart', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'product', 'cart', ['card_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'product', type_='foreignkey')
    op.drop_column('product', 'quantity_in_cart')
    op.drop_column('product', 'card_id')
    op.drop_constraint(None, 'cart', type_='foreignkey')
    op.drop_column('cart', 'user_id')
    # ### end Alembic commands ###
