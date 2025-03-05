from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Field

# Entidade de contrato
class Contract(SQLModel, table=True):
    __tablename__ = "contracts"  # Table name
    
    id: int = Field(default=None, primary_key=True)
    numero_contrato: Optional[str] = Field(default=None)
    cpf_cnpj: Optional[str] = Field(default=None)
    contratante: Optional[str] = Field(default=None)
    contratado: Optional[str] = Field(default=None)
    tipo_objeto: Optional[str] = Field(default=None)
    objeto: Optional[str] = Field(default=None)

    values: List["ContractValues"] = Relationship(back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    dates: List["ContractDates"] = Relationship(back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    administrative_process: List["AdministrativeProcess"] = Relationship(back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete-orphan"})