from sqlmodel import SQLModel, Field

# Entidade de valores de contrato
class ContractValues(SQLModel, table=True):
    __tablename__ = "contract_values"  # Table name
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id") # Foreign key to Contract