from sqlmodel import SQLModel, Field

# Entidade de processos administrativos
class AdministrativeProcess(SQLModel, table=True):
    __tablename__ = "administrative_processes"  # Table name
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id") # Foreign key to Contract