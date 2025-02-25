from sqlmodel import SQLModel, Field, Relationship

# Entidade de valores de convênio
class AgreementValues(SQLModel, table=True):
    __tablename__ = "agreement_values"  # Table name
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id", ondelete='CASCADE') # Foreign key to Agreement
    valor_inicial_total: float
    valor_inicial_repasse_concedente: float
    valor_inicial_contrapartida_convenente: float
    valor_atualizado_total: float
    valor_pago: float
    
    agreement: "Agreement" = Relationship(back_populates="values")  # Relationship with Agreement