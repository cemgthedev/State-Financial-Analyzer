from sqlmodel import SQLModel, Field, Relationship

# Entidade de valores de convênio
class AgreementValues(SQLModel, table=True):
    __tablename__ = "agreement_values"  # Table name
    id: int = Field(default=None, primary_key=True)
    agreement_id: int = Field(foreign_key="agreements.id", ondelete='CASCADE') # Foreign key to Agreement
    valor_inicial_total: float = Field(default=None, nullable=True)
    valor_inicial_repasse_concedente: float = Field(default=None, nullable=True)
    valor_inicial_contrapartida_convenente: float = Field(default=None, nullable=True)
    valor_atualizado_total: float = Field(default=None, nullable=True)
    valor_pago: float = Field(default=None, nullable=True)
    
    agreement: "Agreement" = Relationship(back_populates="values")  # Relationship with Agreement