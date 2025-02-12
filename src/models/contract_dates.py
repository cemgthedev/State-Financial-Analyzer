from sqlmodel import SQLModel, Field

# Entidade de datas de contrato
class ContractDates(SQLModel, table=True):
    __tablename__ = "contract_dates"  # Table name
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id") # Foreign key to Contract