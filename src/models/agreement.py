from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

# Entidade de convênio
class Agreement(SQLModel, table=True):
    __tablename__ = "agreements"  # Table name
    id: int = Field(default=None, primary_key=True)
    codigo_plano_trabalho: str = Field(default=None, nullable=True)
    concedente: str = Field(default=None, nullable=True)
    convenente: str = Field(default=None, nullable=True)
    objeto: str = Field(default=None, nullable=True)
    
    values: "AgreementValues" = Relationship(back_populates="agreement", cascade_delete=True)  # Relationship with AgreementValues
    account: "Accountability" = Relationship(back_populates="agreement", cascade_delete=True) # Relationship with Accountability
    dates: "AgreementDates" = Relationship(back_populates='agreement', cascade_delete=True) # Relationship with AgreementDates