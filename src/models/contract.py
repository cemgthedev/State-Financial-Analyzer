from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field

# Entidade de contrato
class Contract(SQLModel, table=True):
    __tablename__ = "contracts"  # Table name
    id: int = Field(default=None, primary_key=True)
    numero_contrato: str = Field(default=None)
    cpf_cnpj: str = Field(default=None)
    contratante: str = Field(default=None)
    contratado: str = Field(default=None)
    tipo_objeto: Optional[str] = Field(default=None)
    objeto: str = Field(default=None)

    values: List["ContractValues"] = Relationship(back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete-orphan"})