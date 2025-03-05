from sqlmodel import Relationship, SQLModel, Field

# Entidade de valores de contrato
class ContractValues(SQLModel, table=True):
    __tablename__ = "contract_values"  # Table name
    
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id", ondelete='CASCADE') # Foreign key to Contract
    valor_original: float
    valor_aditivo: float
    valor_atualizado: float
    valor_empenhado: float
    valor_pago: float
    
    contract: "Contract" = Relationship(back_populates="values")