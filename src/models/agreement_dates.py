from sqlmodel import SQLModel, Field
from datetime import date  # Importe o tipo date

# Entidade de datas de convênio
class AgreementDates(SQLModel, table=True):
    __tablename__ = "agreement_dates"  # Table name
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id")  # Foreign key to Agreement
    data_assinatura: date = Field(nullable=True)  # Data de assinatura (pode ser nula)
    data_termino: date = Field(nullable=True)  # Data de término (pode ser nula)
    data_publi_ce: date = Field(nullable=True)  # Data de publicação no CE (pode ser nula)
    data_publi_doe: date = Field(nullable=True)  # Data de publicação no DOE (pode ser nula)

    agreement: "Agreement" = Relationship(back_populates="dates")  # Relacionamento com Agreement
