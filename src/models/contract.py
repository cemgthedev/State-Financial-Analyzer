from sqlmodel import SQLModel, Field

# Entidade de contrato
class Contract(SQLModel, table=True):
    __tablename__ = "contracts"  # Table name
    id: int = Field(default=None, primary_key=True)