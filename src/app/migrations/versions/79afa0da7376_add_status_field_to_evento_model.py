"""Add status field to Evento model

Revision ID: 79afa0da7376
Revises: c06096448c52
Create Date: 2025-04-03 21:10:49.623861

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '79afa0da7376'
down_revision = 'c06096448c52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('palestrantes')
    op.drop_table('eventos_palestrantes')
    with op.batch_alter_table('eventos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('eventos', schema=None) as batch_op:
        batch_op.drop_column('status')

    op.create_table('eventos_palestrantes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('evento_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('palestrante_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('papel', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('ordem_apresentacao', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('horario_apresentacao', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['evento_id'], ['eventos.id'], name='eventos_palestrantes_ibfk_1'),
    sa.ForeignKeyConstraint(['palestrante_id'], ['palestrantes.id'], name='eventos_palestrantes_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('palestrantes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('nome', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=120), nullable=False),
    sa.Column('bio', mysql.TEXT(), nullable=True),
    sa.Column('area_atuacao', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('foto_url', mysql.VARCHAR(length=200), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='palestrantes_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
