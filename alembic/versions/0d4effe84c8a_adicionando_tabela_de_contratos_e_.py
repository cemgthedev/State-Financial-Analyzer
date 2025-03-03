"""Adicionando tabela de contratos e valores de contratos

Revision ID: 0d4effe84c8a
Revises: 13870e6ef705
Create Date: 2025-03-03 19:30:23.699012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0d4effe84c8a'
down_revision: Union[str, None] = '13870e6ef705'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Criando colunas na tabela contract_values
    op.add_column('contract_values', sa.Column('valor_original', sa.Float(), nullable=False))
    op.add_column('contract_values', sa.Column('valor_aditivo', sa.Float(), nullable=False))
    op.add_column('contract_values', sa.Column('valor_atualizado', sa.Float(), nullable=False))
    op.add_column('contract_values', sa.Column('valor_empenhado', sa.Float(), nullable=False))
    op.add_column('contract_values', sa.Column('valor_pago', sa.Float(), nullable=False))
    
    # Ajustando chave estrangeira de contract_values para contracts
    op.drop_constraint('contract_values_contract_id_fkey', 'contract_values', type_='foreignkey')
    op.create_foreign_key('contract_values_contract_id_fkey', 'contract_values', 'contracts', ['contract_id'], ['id'], ondelete='CASCADE')
    
    # Criando colunas na tabela contracts
    op.add_column('contracts', sa.Column('numero_contrato', sa.String(), nullable=False))
    op.add_column('contracts', sa.Column('cpf_cnpj', sa.String(), nullable=False))
    op.add_column('contracts', sa.Column('contratante', sa.String(), nullable=False))
    op.add_column('contracts', sa.Column('contratado', sa.String(), nullable=False))
    op.add_column('contracts', sa.Column('tipo_objeto', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('objeto', sa.String(), nullable=False))

def downgrade() -> None:
    # Removendo colunas da tabela contracts
    op.drop_column('contracts', 'objeto')
    op.drop_column('contracts', 'tipo_objeto')
    op.drop_column('contracts', 'contratado')
    op.drop_column('contracts', 'contratante')
    op.drop_column('contracts', 'cpf_cnpj')
    op.drop_column('contracts', 'numero_contrato')
    
    # Restaurando chave estrangeira original de contract_values
    op.drop_constraint('contract_values_contract_id_fkey', 'contract_values', type_='foreignkey')
    op.create_foreign_key('contract_values_contract_id_fkey', 'contract_values', 'contracts', ['contract_id'], ['id'])
    
    # Removendo colunas da tabela contract_values
    op.drop_column('contract_values', 'valor_pago')
    op.drop_column('contract_values', 'valor_empenhado')
    op.drop_column('contract_values', 'valor_atualizado')
    op.drop_column('contract_values', 'valor_aditivo')
    op.drop_column('contract_values', 'valor_original')