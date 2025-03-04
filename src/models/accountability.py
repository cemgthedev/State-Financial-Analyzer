from sqlmodel import SQLModel, Field

# Entidade de prestação de contas de convênio
class Accountability(SQLModel, table=True):
    __tablename__ = "accountability"  # Table name
    
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id")  # Relacionamento com o Convênio
    
    status: str = Field(description="Status da prestação de contas")  # Ex: 'Pendente', 'Aprovado', 'Rejeitado'
    justification: str = Field(default=None, description="Justificativa caso rejeitado")  # Explicação da rejeição
    report_type: str = Field(description="Tipo de prestação de contas")  # Ex: 'Parcial' ou 'Final'
    notes: str = Field(default=None, description="Notas adicionais")  # Informações complementares
