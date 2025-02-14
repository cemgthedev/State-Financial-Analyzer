from sqlmodel import SQLModel, Field

# Entidade de valores de convênio
class AgreementValues(SQLModel, table=True):
    __tablename__ = "agreement_values"  # Table name
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id") # Foreign key to Agreement