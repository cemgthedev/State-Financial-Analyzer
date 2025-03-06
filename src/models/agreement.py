from sqlmodel import SQLModel, Field, Relationship

# Entidade de convênio
class Agreement(SQLModel, table=True):
    __tablename__ = "agreements"  # Table name
    id: int = Field(default=None, primary_key=True)
    codigo_plano_trabalho: str = Field(default=None)
    concedente: str = Field(default=None)
    convenente: str = Field(default=None)
    objeto: str = Field(default=None)
    
    values: "AgreementValues" = Relationship(back_populates="agreement", cascade_delete=True)  # Relationship with AgreementValues
    account: "Accountability" = Relationship(back_populates="agreement", cascade_delete=True) # Relationship with Accountability
    dates: "AgreementDates" = Relationship(back_populates='agreement', cascade_delete=True) # Relationship with AgreementDates