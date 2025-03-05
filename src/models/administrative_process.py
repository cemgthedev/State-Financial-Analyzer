from typing import Optional
from sqlmodel import Relationship, SQLModel, Field

class AdministrativeProcess(SQLModel, table=True):
    __tablename__ = "administrative_processes"  # Table name
    
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id", ondelete='CASCADE') # Foreign key to Contract
    n_do_processo_spu: Optional[str] = Field(default=None)
    modalidade_de_licitacao: Optional[str] = Field(default=None)
    justificativa: Optional[str] = Field(default=None)
    status_do_instrumento: Optional[str] = Field(default=None)
    situacao_fisica: Optional[str] = Field(default=None)
    
    contract: "Contract" = Relationship(back_populates="administrative_process")
