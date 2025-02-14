from sqlmodel import SQLModel, Field

# Entidade de prestação de contas de convênio
class Accountability(SQLModel, table=True):
    __tablename__ = "accountability"  # Table name
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id") # Foreign key to Agreement