from sqlmodel import SQLModel, Field

# Entidade de datas de convênio
class AgreementDates(SQLModel, table=True):
    __tablename__ = "agreement_dates"  # Table name
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id") # Foreign key to Agreement